from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _


class SendEmail:
    def __init__(self, user: User):
        self.user = user
        self.token = default_token_generator.make_token(self.user)
        self.uid = urlsafe_base64_encode(str(self.user.pk).encode())

    def send_activate_email(self):
        # reset_password_url = reverse_lazy(
        #     "authapp:signup_confirm", kwargs={"uidb64": self.uid, "token": self.token}
        # )
        subject = _("Activating an account on the site XXX")
        message = _("Thank you for registering on the site XXX.\n"
            "To activate your account, please follow the link:\n"
            "http://0.0.0.0:8000{reset_password_url}\n"
        )
        final_message = message.format(
            reset_password_url=reverse_lazy(
                "authapp:signup_confirm", kwargs={"uidb64": self.uid, "token": self.token}
            )
        )

        self.user.email_user(subject=subject, message=final_message)


def activate_email_task(user: User):
    send_email = SendEmail(user=user)
    send_email.send_activate_email()
