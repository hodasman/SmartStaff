from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailChangeTokenGenerator(PasswordResetTokenGenerator):
    """Токен подтверждения смены email.

    Отдельный key_salt: токен не взаимозаменяем с токенами сброса пароля
    и активации аккаунта. Включает текущие email и new_email: любое
    изменение адресов делает старую ссылку невалидной."""

    key_salt = "authapp.tokens.EmailChangeTokenGenerator"

    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk) + user.email + (user.new_email or "") + str(timestamp)
        )


email_change_token_generator = EmailChangeTokenGenerator()
