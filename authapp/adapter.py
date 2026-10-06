"""Адаптер allauth под нашу модель User.

Нюанс: username в проекте ASCII, max_length=15, а дефолтный адаптер
allauth генерирует username из email/имени без учёта этого лимита —
получил бы IntegrityError на вставке. Адаптер режет основу и добавляет
случайный суффикс, гарантируя уникальность.
"""
import random
import re
import string

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model


USERNAME_MAX_LENGTH = 15


class AccountAdapter(DefaultAccountAdapter):

    def generate_unique_username(self, txts, regex=None):
        User = get_user_model()

        base = re.sub(r"[^a-zA-Z0-9_.@+-]", "", "-".join(txts)) or "user"
        base = base[: USERNAME_MAX_LENGTH - 4]
        base = base.lstrip("-._@+")

        for _ in range(30):
            suffix = "".join(
                random.choices(string.ascii_lowercase + string.digits, k=4)
            )
            candidate = f"{base}{suffix}"[:USERNAME_MAX_LENGTH]
            if not User.objects.filter(username__iexact=candidate).exists():
                return candidate
        # 30 уникальных вариантов не нашли (почти невероятно):
        # отдаём дефолтному адаптеру право добить
        return super().generate_unique_username(txts, regex)


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """Соц-вход: юзер создаётся сразу активным.

    Наша модель намеренно имеет is_active default=False (своя активация
    по письму). Дефолтный allauth-адаптер создаёт юзера через модель,
    минуя UserManager.create_user, — и соц-юзер оставался неактивным
    ("Аккаунт неактивен" сразу после входа). Email соц-аккаунта уже
    проверен провайдером, поэтому активируем сразу. Собственная
    почтовая активация (RegisterView) не затрагивается.
    """

    def save_user(self, request, sociallogin, form=None):
        # сигнатура соц-адаптера принимает sociallogin (не user)
        sociallogin.user.is_active = True
        return super().save_user(request, sociallogin, form)
