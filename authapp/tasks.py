import logging
from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext as _

if TYPE_CHECKING:
    from authapp.models import User

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


def activate_email_task(request, user: AbstractBaseUser):
    send_email = SendEmail(request=request, user=user)
    send_email.send_activate_email()