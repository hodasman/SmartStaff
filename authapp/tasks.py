from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_encode


class SendEmail:
    def __init__(self, user: User):
        self.user = user
        self.token = default_token_generator.make_token(self.user)
        self.uid = urlsafe_base64_encode(str(self.user.pk).encode())

    def send_activate_email(self):
        reset_password_url = reverse_lazy(
            "authapp:signup_confirm", kwargs={"uidb64": self.uid, "token": self.token}
        )
        subject = f"Активация аккаунта на сайте "
        message = (
            f"Благодарим за регистрацию на сайте .\n"
            "Для активации учётной записи, пожалуйста перейдите по ссылке:\n"
            f"http://0.0.0.0:8000{reset_password_url}\n"
        )

        self.user.email_user(subject=subject, message=message)


def activate_email_task(user: User):
    send_email = SendEmail(user=user)
    send_email.send_activate_email()
