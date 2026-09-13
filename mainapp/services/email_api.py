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
