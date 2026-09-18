"""Отправка почты через HTTPS API Brevo (https://brevo.com).

Railway блокирует исходящий SMTP (порты 25/465/587) — любые SMTP-отправки
из контейнера падают с "Network is unreachable". API ходит через HTTPS:443
и работает без ограничений.

Включение на проде: задать env BREVO_API_KEY — settings.py сам переключит
EMAIL_BACKEND на этот класс. Локально без ключа продолжает работать SMTP.
"""
import logging

import requests
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)

BREVO_API_URL = 'https://api.brevo.com/v3/smtp/email'
BREVO_TIMEOUT = 15  # секунды


class BrevoEmailBackend(BaseEmailBackend):
    """Django email backend, отправляющий письма через REST API Brevo."""

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        api_key = getattr(settings, 'BREVO_API_KEY', '')
        if not api_key:
            raise RuntimeError(
                'BREVO_API_KEY не задан:BrevoEmailBackend не может отправить письма'
            )

        sent = 0
        for message in email_messages:
            if self._send_one(message, api_key):
                sent += 1
            elif not self.fail_silently:
                # повторяем поведение SMTP-бэкенда: без fail_silently падаем сразу
                raise RuntimeError('Brevo API: письмо не отправлено (см. логи)')
        return sent

    def _send_one(self, message, api_key):
        payload = self._build_payload(message)
        try:
            response = requests.post(
                BREVO_API_URL,
                json=payload,
                headers={
                    'api-key': api_key,
                    'accept': 'application/json',
                    'content-type': 'application/json',
                },
                timeout=BREVO_TIMEOUT,
            )
        except requests.RequestException:
            logger.exception('Brevo API недоступен: письмо на %s не отправлено', message.to)
            return False

        if response.status_code == 201:
            logger.info('Brevo: письмо на %s отправлено', message.to)
            return True

        logger.error(
            'Brevo API вернул %s: %s — письмо на %s не отправлено',
            response.status_code, response.text[:300], message.to,
        )
        return False

    def _build_payload(self, message):
        from_email = message.from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', '')
        payload = {
            'sender': {'email': from_email},
            'to': [{'email': addr} for addr in message.to],
            'subject': message.subject,
        }
        if message.bcc:
            payload['bcc'] = [{'email': addr} for addr in message.bcc]
        if message.cc:
            payload['cc'] = [{'email': addr} for addr in message.cc]
        if message.reply_to:
            payload['replyTo'] = {'email': message.reply_to[0]}
        if message.content_subtype == 'html':
            payload['htmlContent'] = message.body
        else:
            payload['textContent'] = message.body
        return payload


SENDPULSE_OAUTH_URL = 'https://api.sendpulse.com/oauth/access_token'
SENDPULSE_SMTP_URL = 'https://api.sendpulse.com/smtp/emails'


class SendPulseEmailBackend(BaseEmailBackend):
    """Отправка писем через HTTPS API SendPulse (порт 443).

    SMTP-порты из Railway-контейнера недоступны, поэтому используется REST API.
    Включается автоматически, если заданы SENDPULSE_CLIENT_ID и
    SENDPULSE_CLIENT_SECRET (Настройки аккаунта SendPulse -> API).
    """

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        client_id = getattr(settings, 'SENDPULSE_CLIENT_ID', '')
        client_secret = getattr(settings, 'SENDPULSE_CLIENT_SECRET', '')
        if not (client_id and client_secret):
            raise RuntimeError(
                'SENDPULSE_CLIENT_ID/SENDPULSE_CLIENT_SECRET не заданы: '
                'SendPulseEmailBackend не может отправить письма'
            )

        token = self._get_token(client_id, client_secret)
        if not token:
            if self.fail_silently:
                return 0
            raise RuntimeError('SendPulse API: не удалось получить токен')

        sent = 0
        for message in email_messages:
            if self._send_one(message, token):
                sent += 1
            elif not self.fail_silently:
                raise RuntimeError('SendPulse API: письмо не отправлено (см. логи)')
        return sent

    def _get_token(self, client_id, client_secret):
        try:
            response = requests.post(
                SENDPULSE_OAUTH_URL,
                json={
                    'grant_type': 'client_credentials',
                    'client_id': client_id,
                    'client_secret': client_secret,
                },
                timeout=BREVO_TIMEOUT,
            )
        except requests.RequestException:
            logger.exception('SendPulse OAuth недоступен')
            return None
        if response.status_code == 200:
            return response.json().get('access_token')
        logger.error(
            'SendPulse OAuth вернул %s: %s', response.status_code, response.text[:300]
        )
        return None

    def _send_one(self, message, token):
        from_email = message.from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', '')
        email_data = {
            'subject': message.subject,
            'from': {'email': from_email},
            'to': [{'email': addr} for addr in message.to],
        }
        if message.content_subtype == 'html':
            email_data['html'] = message.body
        else:
            email_data['text'] = message.body
        if message.bcc:
            email_data['bcc'] = [{'email': addr} for addr in message.bcc]
        if message.cc:
            email_data['cc'] = [{'email': addr} for addr in message.cc]

        try:
            response = requests.post(
                SENDPULSE_SMTP_URL,
                json={'email': email_data},
                headers={'Authorization': 'Bearer %s' % token},
                timeout=BREVO_TIMEOUT,
            )
        except requests.RequestException:
            logger.exception('SendPulse API недоступен: письмо на %s не отправлено', message.to)
            return False

        if response.status_code == 200 and response.json().get('result'):
            logger.info('SendPulse: письмо на %s отправлено', message.to)
            return True
        logger.error(
            'SendPulse API вернул %s: %s — письмо на %s не отправлено',
            response.status_code, response.text[:300], message.to,
        )
        return False
