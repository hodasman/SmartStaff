import logging
from typing import TYPE_CHECKING

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext as _

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class SendEmail:
    def __init__(self, request, user: AbstractBaseUser):
        self.request = request
        self.user = user
        self.token = default_token_generator.make_token(self.user)
        self.uid = urlsafe_base64_encode(str(self.user.pk).encode())

    def send_activate_email(self):
        activate_url = reverse(
            "authapp:signup_confirm",
            kwargs={"uidb64": self.uid, "token": self.token},
        )
        # Абсолютная ссылка строится от текущего запроса:
        # локально это http://127.0.0.1:8000/..., на проде — реальный домен
        absolute_url = self.request.build_absolute_uri(activate_url)
        site_name = get_current_site(self.request).name

        subject = _("Activating an account on the site %s") % site_name
        message = _(
            "Thank you for registering on the site %(site_name)s.\n"
            "To activate your account, please follow the link:\n%(link)s\n"
        ) % {"site_name": site_name, "link": absolute_url}

        self.user.email_user(subject=subject, message=message)


    def send_email_change_email(self):
        """Письмо с подтверждением смены email на адрес user.new_email."""
        # Токен ДЛЯ СМЕНЫ EMAIL строит EmailChangeTokenGenerator, а не
        # default_token_generator: генераторы имеют разные key_salt, вьюха
        # подтверждения проверяет именно этот.
        from django.utils.http import urlsafe_base64_encode

        from authapp.tokens import email_change_token_generator
        uid = urlsafe_base64_encode(str(self.user.pk).encode())
        token = email_change_token_generator.make_token(self.user)
        change_url = reverse(
            "authapp:email_change_confirm",
            kwargs={"uidb64": uid, "token": token},
        )
        absolute_url = self.request.build_absolute_uri(change_url)

        subject = _("Confirm your new email address")
        message = _(
            "You (or someone) requested changing the email address for your "
            "account on %(site_name)s to %(new_email)s.\n"
            "To confirm the new address, please follow the link:\n%(link)s\n"
            "If you did not request this, just ignore this email — your "
            "current address will remain unchanged.\n"
        ) % {
            "site_name": get_current_site(self.request).name,
            "new_email": self.user.new_email,
            "link": absolute_url,
        }
        # Письмо уходит на НОВЫЙ адрес (кандидат), а не на текущий
        from django.core.mail import send_mail
        send_mail(subject, message, None, [self.user.new_email])


def activate_email_task(request, user: AbstractBaseUser):
    send_email = SendEmail(request=request, user=user)
    send_email.send_activate_email()


def email_change_task(request, user: AbstractBaseUser):
    send_email = SendEmail(request=request, user=user)
    send_email.send_email_change_email()
