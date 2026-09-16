from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def send_contact_email_message(subject, email, content, ip, user_id, name):
    """
    Функция для отправки электронного письма из формы обратной связи сайта
    """
    User = get_user_model()
    user = User.objects.get(id=user_id) if user_id else None
    message = render_to_string('mainapp/feedback_email_send.html', {
        'email': email,
        'content': content,
        'ip': ip,
        'user': user,
        'name': name,
    })
    # адрес отправителя — DEFAULT_FROM_EMAIL (почта на домене сайта),
    # а не EMAIL_HOST_USER (это логин SMTP-провайдера)
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', '') or settings.EMAIL_HOST_USER
    email = EmailMessage(subject, message, from_email, [settings.EMAIL_ADMIN])
    email.send(fail_silently=False)