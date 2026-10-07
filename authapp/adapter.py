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
        user = super().save_user(request, sociallogin, form)
        self._enrich_from_yandex(user, sociallogin)
        return user

    def _enrich_from_yandex(self, user, sociallogin):
        """Дополнительные поля из ответа Яндекса (login.yandex.ru/info):
        дата рождения -> date_of_birth, портрет -> avatar.
        first_name/last_name/email маппит сам allauth (extract_common_fields).
        Пол (sex) Яндекс отдаёт, но в модели поля нет — не сохраняем.
        Заполняем ТОЛЬКО пустые поля и только при первом создании юзера.
        """
        # ВАЖНО: SocialLogin.deserialize НЕ восстанавливает атрибут
        # .provider (потеряется при session round-trip) — надёжный
        # источник провайдера: account.provider (строка в БД)
        provider_id = sociallogin.account.provider
        if provider_id != "yandex":
            return
        extra = sociallogin.account.extra_data or {}
        changed = []

        if not user.date_of_birth and extra.get("birthday"):
            try:
                y, m, d = (int(x) for x in str(extra["birthday"]).split("-"))
                from datetime import date
                if 1900 <= y <= date.today().year:
                    user.date_of_birth = date(y, m, d)
                    changed.append("date_of_birth")
            except (ValueError, TypeError):
                pass

        if not user.avatar and extra.get("avatar"):
            if self._fetch_yandex_avatar(user, str(extra["avatar"])):
                changed.append("avatar")

        if changed:
            user.save(update_fields=changed)

    def _fetch_yandex_avatar(self, user, avatar_id):
        """Скачивает портрет с avatars.yandex.net. Любая ошибка сети —
        тихий пропуск: аватар не критичен для регистрации."""
        import requests
        from django.core.files.base import ContentFile

        try:
            resp = requests.get(
                f"https://avatars.yandex.net/get-yandex-avatars/{avatar_id}/200x200",
                timeout=5,
            )
            resp.raise_for_status()
            content_type = resp.headers.get("Content-Type", "")
            if not content_type.startswith("image/") or len(resp.content) > 2 * 1024 * 1024:
                return False
            user.avatar.save(
                f"{user.username}_yandex.jpg",
                ContentFile(resp.content),
                save=False,
            )
            return True
        except (requests.RequestException, OSError):
            return False
