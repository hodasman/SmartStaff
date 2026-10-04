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
