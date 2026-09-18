import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)


def send_subscribe_confirm_email(email):
    """
    Отправляет письмо-подтверждение после подписки на рассылку.
    Письмо уходит на адрес подписчика от EMAIL_HOST_USER.
    Вызывается из фонового потока, поэтому все ошибки ловим внутри:
    недоступный SMTP не должен ронять процесс.
    """
    try:
        subject = _('You have subscribed to the newsletter!')
        message = render_to_string(
            'subscribeapp/subscribe_confirm_email.html',
            {'email': email},
        )
        # адрес отправителя — DEFAULT_FROM_EMAIL (почта на домене сайта),
        # а не EMAIL_HOST_USER (это логин SMTP-провайдера)
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', '') or settings.EMAIL_HOST_USER
        letter = EmailMessage(subject, message, from_email, [email])
        letter.content_subtype = 'html'
        letter.send(fail_silently=False)
    except Exception:
        logger.exception(
            'Не удалось отправить письмо о подписке на %s (backend=%s, host=%s:%s)',
            email, settings.EMAIL_BACKEND, settings.EMAIL_HOST, settings.EMAIL_PORT,
        )
