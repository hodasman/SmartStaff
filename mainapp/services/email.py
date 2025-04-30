from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def send_contact_email_message(subject, email, content, ip, user_id, name):
    """
    Функция для отправки электронного письма из формы обратной связи сайта
    """
    user = User.objects.get(id=user_id) if user_id else None
    message = render_to_string('mainapp/feedback_email_send.html', {
        'email': email,
        'content': content,
        'ip': ip,
        'user': user,
        'name': name,
    })
    email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [settings.EMAIL_ADMIN])
    email.send(fail_silently=False)