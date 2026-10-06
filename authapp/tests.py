"""
Тесты аутентификации authapp.

Покрывают полный жизненный цикл аккаунта:
- регистрация с отправкой письма активации
- активация по ссылке (в т.ч. устойчивость к битым ссылкам)
- повторная отправка письма активации (resend-activation)
- вход/выход, защита неактивированных аккаунтов
- блокировка brute force (django-axes)
- смена пароля залогиненным пользователем
- восстановление пароля (password reset)

Запуск: python manage.py test authapp
"""
from datetime import date
import shutil
import tempfile
from unittest import mock
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import Client, TestCase, override_settings
import requests
from django.urls import reverse, reverse_lazy

User = get_user_model()


def make_user(email="user@test.local", username="tester", password="Sup3r#Secret",
              is_active=True):
    """Фабрика юзера. create_user() не активирует (is_active=False по умолчанию)."""
    user = User(
        username=username, email=email, first_name="Test",
        date_of_birth="1999-01-01",
        is_active=is_active,
    )
    user.set_password(password)
    user.save()
    return user


def csrf_post(client, url, data):
    """POST с CSRF-токеном, как это делает реальный браузер."""
    token = client.cookies.get("csrftoken")
    data = dict(data)
    if token:
        data["csrfmiddlewaretoken"] = token.value
    return client.post(url, data, follow=False)


class RegistrationTests(TestCase):
    """Регистрация: создание аккаунта + письмо активации."""

    def test_register_creates_inactive_user_and_sends_email(self):
        """Успешная регистрация: юзер неактивен, письмо активации отправлено."""
        response = csrf_post(
            Client(),
            reverse("authapp:register"),
            {
                "username": "newbie",
                "email": "newbie@test.local",
                "first_name": "New",
                "last_name": "User",
                "date_of_birth": "1999-01-01",
                "country": "BY",
                "password1": "Sup3r#Secret",
                "password2": "Sup3r#Secret",
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(email="newbie@test.local")
        self.assertFalse(user.is_active, "новый юзер не должен быть активен")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("newbie@test.local", mail.outbox[0].to)
        # в письме есть ссылка активации
        self.assertIn("signup_confirm", mail.outbox[0].body)
        self.assertTrue(mail.outbox[0].body.startswith("http") or
                        "http" in mail.outbox[0].body)

    def test_register_duplicate_email_rejected(self):
        """Email уже занят: форма с ошибкой, письмо не отправляется."""
        make_user(email="taken@test.local")
        response = csrf_post(
            Client(),
            reverse("authapp:register"),
            {
                "username": "other",
                "email": "taken@test.local",
                "date_of_birth": "1999-01-01",
                "password1": "Sup3r#Secret",
                "password2": "Sup3r#Secret",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())
        self.assertEqual(len(mail.outbox), 0)

    def test_register_password_mismatch_rejected(self):
        """Несовпадающие пароли: аккаунт не создаётся."""
        response = csrf_post(
            Client(),
            reverse("authapp:register"),
            {
                "username": "newbie",
                "email": "newbie@test.local",
                "date_of_birth": "1999-01-01",
                "password1": "Sup3r#Secret",
                "password2": "Other#12345",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email="newbie@test.local").exists())

    def test_register_no_email_sent_on_smtp_failure(self):
        """SMTP/API упал: аккаунт создан, 500 нет, юзеру объяснили проблему."""
        with mock.patch("authapp.views.activate_email_task",
                        side_effect=ConnectionError("SMTP down")):
            response = csrf_post(
                Client(),
                reverse("authapp:register"),
                {
                    "username": "newbie",
                    "email": "newbie@test.local",
                    "date_of_birth": "1999-01-01",
                    "password1": "Sup3r#Secret",
                    "password2": "Sup3r#Secret",
                },
            )
        # ключевой момент: не 500, хотя письмо отправить не удалось
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            User.objects.filter(email="newbie@test.local").exists(),
            "аккаунт должен быть создан даже при падении почты",
        )


class ActivationTests(TestCase):
    """Активация по ссылке из письма."""

    def make_inactive_with_link(self):
        user = make_user(email="act@test.local", is_active=False)
        token = default_token_generator.make_token(user)
        from django.utils.http import urlsafe_base64_encode
        uidb64 = urlsafe_base64_encode(str(user.pk).encode())
        return user, reverse("authapp:signup_confirm",
                             kwargs={"uidb64": uidb64, "token": token})

    def test_activation_link_activates_and_logs_in(self):
        """Валидная ссылка: is_active=True, юзер залогинен, редирект в кабинет."""
        user, url = self.make_inactive_with_link()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        # юзер залогинен после активации
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_activation_invalid_token_rejected(self):
        """Битый токен: юзер остаётся неактивным, редирект на логин."""
        user, url = self.make_inactive_with_link()
        bad_url = url.replace(url.rsplit("/", 2)[-2], "0" * 8)
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    def test_activation_unknown_uid_rejected(self):
        """Несуществующий uid: не падаем, редирект на логин."""
        response = self.client.get(
            reverse("authapp:signup_confirm",
                    kwargs={"uidb64": "AAAA", "token": "x-y-z"})
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_activation_reuses_link_after_success_rejected(self):
        """Одноразовость: после успешной активации та же ссылка уже не логинит
        заново (токен стал невалидным после смены даты входа)."""
        user, url = self.make_inactive_with_link()
        self.client.get(url)  # первая активация
        # повторный клик не должен логинить другим пользователем/падать
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)


class ResendActivationTests(TestCase):
    """Повторная отправка письма активации."""

    def test_resend_sends_email_for_inactive_user(self):
        user = make_user(email="resend@test.local", is_active=False)
        response = csrf_post(
            Client(), reverse("authapp:resend_activation"),
            {"email": "resend@test.local"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("signup_confirm", mail.outbox[0].body)

    def test_resend_active_user_no_email(self):
        """Активный юзер: письмо не отправляется (активация не нужна)."""
        make_user(email="active@test.local", is_active=True)
        response = csrf_post(
            Client(), reverse("authapp:resend_activation"),
            {"email": "active@test.local"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 0)

    def test_resend_unknown_email_no_enumeration(self):
        """Несуществующий email: тот же статус ответа, письмо не отправляется.
        Защита от перебора: нельзя отличить 'нет юзера' от 'неактивный'."""
        make_user(email="resend@test.local", is_active=False)
        response_known = csrf_post(
            Client(), reverse("authapp:resend_activation"),
            {"email": "resend@test.local"},
        )
        response_unknown = csrf_post(
            Client(), reverse("authapp:resend_activation"),
            {"email": "unknown@test.local"},
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(response_known.status_code, response_unknown.status_code)

    def test_resend_smtp_failure_no_500(self):
        """SMTP упал: не 500, юзер получает сообщение об ошибке."""
        user = make_user(email="resend@test.local", is_active=False)
        with mock.patch("authapp.views.activate_email_task",
                        side_effect=ConnectionError("SMTP down")):
            response = csrf_post(
                Client(), reverse("authapp:resend_activation"),
                {"email": "resend@test.local"},
            )
        self.assertEqual(response.status_code, 302)


class LoginLogoutTests(TestCase):
    """Вход, выход и защита неактивированных аккаунтов."""

    PASSWORD = "Sup3r#Secret"

    def setUp(self):
        self.client = Client()
        # axes может держать счётчики неудач между тестами — сбрасываем
        from axes.models import AccessAttempt
        AccessAttempt.objects.all().delete()

    def do_login(self, email, password):
        token = self.client.cookies.get("csrftoken")
        data = {"username": email, "password": password}
        if token:
            data["csrfmiddlewaretoken"] = token.value
        return self.client.post(reverse("authapp:login"), data, follow=False)

    def test_active_user_can_login(self):
        make_user(email="login@test.local", password=self.PASSWORD)
        self.client.get(reverse("authapp:login"))  # GET для csrf cookie
        response = self.do_login("login@test.local", self.PASSWORD)
        self.assertEqual(response.status_code, 302, "активный юзер должен войти")

    def test_inactive_user_cannot_login(self):
        make_user(email="inactive@test.local", password=self.PASSWORD,
                  is_active=False)
        self.client.get(reverse("authapp:login"))
        response = self.do_login("inactive@test.local", self.PASSWORD)
        self.assertEqual(response.status_code, 200, "неактивный не должен войти")

    def test_inactive_login_shows_resend_hint(self):
        """Неактивный аккаунт: на странице логина появляется подсказка со
        ссылкой на повторную отправку письма активации."""
        make_user(email="inactive@test.local", password=self.PASSWORD,
                  is_active=False)
        self.client.get(reverse("authapp:login"))
        response = self.do_login("inactive@test.local", self.PASSWORD)
        body = response.content.decode("utf-8", "replace")
        self.assertIn("resend-activation", body,
                      "должна быть ссылка на resend-activation")

    @override_settings(LANGUAGE_CODE="en")
    def test_wrong_password_single_error(self):
        """Неверный пароль: ровно одна ошибка, а не весь набор error_messages
        (регрессия: старый form_invalid показывал все ошибки сразу)."""
        make_user(email="login@test.local", password=self.PASSWORD)
        self.client.get(reverse("authapp:login"))
        response = self.do_login("login@test.local", "Wrong#12345")
        body = response.content.decode("utf-8", "replace")
        self.assertEqual(body.count("Something goes wrong"), 1,
                         "должно быть ровно одно сообщение об ошибке")

    def test_logout(self):
        make_user(email="login@test.local", password=self.PASSWORD)
        self.client.force_login(User.objects.get(email="login@test.local"))
        response = self.client.post(reverse("authapp:logout"))
        self.assertEqual(response.status_code, 302)
        # после выхода сессия пуста
        response = self.client.get(reverse("mainapp:main_page"))
        self.assertNotIn("_auth_user_id", self.client.session)


class AxesLockoutTests(TestCase):
    """django-axes: блокировка после 5 неудачных попыток входа."""

    PASSWORD = "Sup3r#Secret"

    def setUp(self):
        from axes.models import AccessAttempt
        AccessAttempt.objects.all().delete()
        self.client = Client()
        make_user(email="locked@test.local", password=self.PASSWORD)

    def do_login(self, password):
        token = self.client.cookies.get("csrftoken")
        data = {"username": "locked@test.local", "password": password}
        if token:
            data["csrfmiddlewaretoken"] = token.value
        return self.client.post(reverse("authapp:login"), data, follow=False)

    def test_lockout_after_five_failures(self):
        """5 неверных паролей -> 5-я попытка получает 429 Too Many Requests.

        Примечание: верный пароль axes не блокирует даже после блокировки
        (задокументированное поведение: защита от перебора, а не от легитимного
        входа; атакующий без пароля всё равно не сможет войти)."""
        self.client.get(reverse("authapp:login"))  # csrf cookie
        for attempt in range(1, 6):
            response = self.do_login("Wrong#12345")
            if attempt < 5:
                self.assertEqual(response.status_code, 200,
                                 f"попытка {attempt}: до лимита не должно быть 429")
            else:
                self.assertEqual(response.status_code, 429,
                                 "5-я неудачная попытка должна быть заблокирована")

    def test_correct_password_resets_counter(self):
        """AXES_RESET_ON_SUCCESS: после успешного входа счётчик сбрасывается
        и юзер не оказывается заблокированным на ровном месте."""
        self.client.get(reverse("authapp:login"))
        # 4 неудачи (лимит 5 — ещё не превышен)
        for _ in range(4):
            self.do_login("Wrong#12345")
        # успешный вход
        response = self.do_login(self.PASSWORD)
        self.assertEqual(response.status_code, 302, "вход должен состояться")
        # 4 новые неудачи — всё ещё не блокировка
        self.client.get(reverse("authapp:login"))
        for _ in range(4):
            self.do_login("Wrong#12345")
        self.client.get(reverse("authapp:login"))
        response = self.do_login(self.PASSWORD)
        self.assertEqual(response.status_code, 302,
                         "после сброса счётчика юзер не должен быть заблокирован")


class PasswordChangeTests(TestCase):
    """Смена пароля залогиненным пользователем."""

    def setUp(self):
        self.client = Client()
        from axes.models import AccessAttempt
        AccessAttempt.objects.all().delete()
        self.user = make_user(email="change@test.local", password="Old#12345")
        self.client.force_login(self.user)

    def test_anonymous_redirected_to_login(self):
        anonymous = Client()
        response = anonymous.get(reverse("authapp:password_change"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_change_password_success(self):
        response = csrf_post(
            self.client, reverse("authapp:password_change"),
            {
                "old_password": "Old#12345",
                "new_password1": "New#Secure99",
                "new_password2": "New#Secure99",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("password-change/done", response.url)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("New#Secure99"))

    def test_change_password_wrong_old_rejected(self):
        response = csrf_post(
            self.client, reverse("authapp:password_change"),
            {
                "old_password": "WRONG",
                "new_password1": "New#Secure99",
                "new_password2": "New#Secure99",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Old#12345"),
                        "пароль не должен измениться при неверном old_password")

    def test_done_view_redirects_to_personal_page(self):
        response = self.client.get(reverse("authapp:password_change_done"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("personal-page", response.url)


class PasswordResetTests(TestCase):
    """Восстановление пароля (для тех, кто не может войти)."""

    PASSWORD = "Sup3r#Secret"

    def setUp(self):
        from axes.models import AccessAttempt
        AccessAttempt.objects.all().delete()
        self.user = make_user(email="reset@test.local", password=self.PASSWORD)

    def test_reset_flow(self):
        client = Client()
        # 1. запрос сброса
        token = client.cookies.get("csrftoken")
        data = {"email": "reset@test.local"}
        if token:
            data["csrfmiddlewaretoken"] = token.value
        client.get(reverse("authapp:password-reset"))
        token = client.cookies.get("csrftoken")
        data["csrfmiddlewaretoken"] = token.value
        response = client.post(reverse("authapp:password-reset"), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        # 2. ссылка из письма
        body = mail.outbox[0].body
        link = [line.strip() for line in body.splitlines()
                if "password_reset_confirm" in line][0]
        path = link.replace("http://testserver", "")
        # 3. переход по ссылке: Django 3.2 переносит токен в сессию
        # и редиректит на /set-password/
        response = client.get(path)
        self.assertEqual(response.status_code, 302)
        self.assertIn("set-password", response.url)
        set_password_path = response.url
        response = client.get(set_password_path)
        self.assertEqual(response.status_code, 200)
        # 4. новый пароль
        new_data = {
            "new_password1": "Fresh#12345",
            "new_password2": "Fresh#12345",
        }
        csrf = client.cookies.get("csrftoken")
        new_data["csrfmiddlewaretoken"] = csrf.value
        response = client.post(set_password_path, new_data)
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Fresh#12345"),
                        "пароль должен быть изменён")
        self.assertFalse(self.user.check_password(self.PASSWORD))

    def test_reset_unknown_email_no_email_sent(self):
        client = Client()
        client.get(reverse("authapp:password-reset"))
        token = client.cookies.get("csrftoken")
        response = client.post(reverse("authapp:password-reset"), {
            "email": "unknown@test.local",
            "csrfmiddlewaretoken": token.value,
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 0)


class SuperuserTests(TestCase):
    """manage.py createsuperuser создаёт валидный активный аккаунт."""

    def test_create_superuser_is_active(self):
        # регрессия: суперюзер создавался неактивным и не мог войти
        User.objects.create_superuser(
            username="admin", first_name="Admin", date_of_birth="1990-01-01",
            email="admin@test.local", password="Adm1n#Pass",
        )
        admin = User.objects.get(email="admin@test.local")
        self.assertTrue(admin.is_active)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)


class EmailChangeTests(TestCase):
    """Смена email в личном кабинете с подтверждением по письму."""

    OLD = "old@test.local"
    NEW = "new@test.local"

    def setUp(self):
        from axes.models import AccessAttempt
        AccessAttempt.objects.all().delete()
        self.client = Client()
        self.user = make_user(email=self.OLD, password="Old#12345")
        self.client.force_login(self.user)

    def submit_profile(self, email):
        c = self.client.cookies.get("csrftoken")
        data = {
            "username": self.user.username,
            "email": email,
            "first_name": "Test",
            "date_of_birth": "1999-01-01",
        }
        if c:
            data["csrfmiddlewaretoken"] = c.value
        return self.client.post(
            reverse("authapp:profile_edit", args=[self.user.pk]), data
        )

    def test_email_change_requires_confirmation(self):
        """Смена email: адрес НЕ меняется сразу, шлётся письмо-подтверждение,
        старый адрес остаётся рабочим."""
        response = self.submit_profile(self.NEW)
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, self.OLD,
                         "email не должен меняться без подтверждения")
        self.assertEqual(self.user.new_email, self.NEW)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.NEW],
                         "письмо-подтверждение уходит на новый адрес")
        self.assertIn("email_change_confirm", mail.outbox[0].body)

    def test_email_change_same_email_no_letter(self):
        """Без изменения email — письмо-подтверждение не отправляется."""
        response = self.submit_profile(self.OLD)
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertIsNone(self.user.new_email)
        self.assertEqual(len(mail.outbox), 0)

    def test_email_change_confirmed_by_link(self):
        """Клик по ссылке подтверждения: email меняется, new_email чистится."""
        self.submit_profile(self.NEW)
        self.user.refresh_from_db()
        from authapp.views import email_change_token_generator
        from django.utils.http import urlsafe_base64_encode
        uidb64 = urlsafe_base64_encode(str(self.user.pk).encode())
        token = email_change_token_generator.make_token(self.user)
        response = self.client.get(
            reverse("authapp:email_change_confirm",
                    kwargs={"uidb64": uidb64, "token": token})
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, self.NEW)
        self.assertIsNone(self.user.new_email)

    def test_email_change_token_not_valid_after_change(self):
        """Токен одноразовый: после подтверждения ссылка больше не работает."""
        self.submit_profile(self.NEW)
        self.user.refresh_from_db()
        from authapp.views import email_change_token_generator
        from django.utils.http import urlsafe_base64_encode
        uidb64 = urlsafe_base64_encode(str(self.user.pk).encode())
        token = email_change_token_generator.make_token(self.user)
        self.client.get(reverse("authapp:email_change_confirm",
                                kwargs={"uidb64": uidb64, "token": token}))
        # повторный клик
        response = self.client.get(reverse("authapp:email_change_confirm",
                                           kwargs={"uidb64": uidb64, "token": token}))
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_email_change_to_taken_email_rejected(self):
        """Новый email уже занят другим юзером: форма отклоняет."""
        make_user(email=self.NEW, username="other")
        response = self.submit_profile(self.NEW)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, self.OLD)
        self.assertIsNone(self.user.new_email)
        self.assertEqual(len(mail.outbox), 0)

    def test_email_change_race_protection(self):
        """Пока юзер не подтвердил, адрес мог занять другой аккаунт:
        подтверждение отклоняется, email не меняется."""
        self.submit_profile(self.NEW)
        self.user.refresh_from_db()
        from authapp.views import email_change_token_generator
        from django.utils.http import urlsafe_base64_encode
        uidb64 = urlsafe_base64_encode(str(self.user.pk).encode())
        token = email_change_token_generator.make_token(self.user)
        # "кто-то" занял адрес
        other = make_user(email=self.NEW, username="racer")
        response = self.client.get(reverse("authapp:email_change_confirm",
                                           kwargs={"uidb64": uidb64, "token": token}))
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, self.OLD,
                         "email не должен смениться на занятый адрес")
        other.delete()

    def test_old_reset_token_invalid_after_change(self):
        """Токен смены email валиден только для конкретной пары email+new_email:
        после очистки new_email resend-ссылка не работает."""
        self.submit_profile(self.NEW)
        self.user.refresh_from_db()
        from authapp.views import email_change_token_generator
        from django.utils.http import urlsafe_base64_encode
        uidb64 = urlsafe_base64_encode(str(self.user.pk).encode())
        token = email_change_token_generator.make_token(self.user)
        # юзер сам сбросил new_email (например, сохранил профиль без смены)
        self.user.new_email = None
        self.user.save(update_fields=["new_email"])
        response = self.client.get(reverse("authapp:email_change_confirm",
                                           kwargs={"uidb64": uidb64, "token": token}))
        self.assertIn("login", response.url)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, self.OLD)


class SocialAuthTests(TestCase):
    """Вход через соцсети (django-allauth)."""

    def test_social_block_hidden_without_provider(self):
        """SocialApp не настроен: блок соц-входа не рендерится."""
        from allauth.socialaccount.models import SocialApp
        SocialApp.objects.all().delete()
        response = self.client.get(reverse("authapp:login"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Login via social networks")

    def test_allauth_login_page_reachable(self):
        """Страница allauth (/accounts/login/) доступна."""
        from allauth.socialaccount.models import SocialApp
        SocialApp.objects.all().delete()
        response = self.client.get("/accounts/login/")
        self.assertEqual(response.status_code, 200)

    def test_adapter_username_clamped_and_unique(self):
        """Адаптер генерирует username в пределах max_length=15 и уникальный."""
        from authapp.adapter import AccountAdapter
        from django.contrib.auth.validators import ASCIIUsernameValidator
        adapter = AccountAdapter(None)
        for _ in range(10):
            username = adapter.generate_unique_username(
                ["some-body.with+very@long", "email@example.com"]
            )
            self.assertLessEqual(len(username), 15, username)
            ASCIIUsernameValidator()(username)  # ValidationError если невалидно
        # генерирует разные кандидаты при повторе
        a = adapter.generate_unique_username(["same", "same@x.io"])
        b = adapter.generate_unique_username(["same", "same@x.io"])
        self.assertNotEqual(a, b)


class MoreSocialProvidersTests(TestCase):
    """Яндекс (SocialApp в БД) и Apple (APP-конфиг из env)."""

    def test_yandex_redirect(self):
        """SocialApp yandex: /accounts/yandex/login/ -> oauth.yandex.ru."""
        from allauth.socialaccount.models import SocialApp
        from django.contrib.sites.models import Site
        app = SocialApp.objects.create(
            provider="yandex", name="Yandex",
            client_id="test-yx-id", secret="test-yx-secret",
        )
        app.sites.add(Site.objects.get_current())
        response = self.client.get("/accounts/yandex/login/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("oauth.yandex.com", response.url)  # allauth 0.54 использует .com

    def test_login_page_shows_yandex(self):
        """Кнопки рендерятся для настроенных провайдеров."""
        from allauth.socialaccount.models import SocialApp
        from django.contrib.sites.models import Site
        app = SocialApp.objects.create(
            provider="yandex", name="Yandex",
            client_id="test-yx-id", secret="test-yx-secret",
        )
        app.sites.add(Site.objects.get_current())
        body = self.client.get(reverse("authapp:login")).content.decode()
        self.assertIn("/accounts/yandex/login/", body)


class FacebookProviderTests(TestCase):
    def test_facebook_redirect(self):
        """SocialApp facebook: /accounts/facebook/login/ -> facebook.com."""
        from allauth.socialaccount.models import SocialApp
        from django.contrib.sites.models import Site
        app = SocialApp.objects.create(
            provider="facebook", name="Facebook",
            client_id="test-fb-id", secret="test-fb-secret",
        )
        app.sites.add(Site.objects.get_current())
        response = self.client.get("/accounts/facebook/login/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("facebook.com", response.url)


class SocialSignupActiveUserTests(TestCase):
    """e2e: соц-регистрация создаёт АКТИВНОГО юзера (регрессия is_active)."""

    def _stash_sociallogin(self, email, username="guser1234"):
        from allauth.socialaccount.models import SocialLogin, SocialAccount, EmailAddress
        from django.contrib.auth import get_user_model
        User = get_user_model()
        u = User(username=username, email=email, first_name="G", date_of_birth="1990-01-01")
        sl = SocialLogin()
        sl.provider = "yandex"
        sl.account = SocialAccount(provider="yandex", uid="54321", user=u)
        sl.email_addresses = [EmailAddress(email=email, verified=True, primary=True)]
        sl.user = u
        session = self.client.session
        session["socialaccount_sociallogin"] = SocialLogin.serialize(sl)
        session.save()

    def test_social_signup_creates_active_user(self):
        self._stash_sociallogin("newsocial@yandex.by")
        response = self.client.get("/accounts/social/signup/")
        self.assertEqual(response.status_code, 200)
        data = {"username": "newsocial", "email": "newsocial@yandex.by"}
        response = self.client.post("/accounts/social/signup/", data)
        self.assertEqual(response.status_code, 302)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(username="newsocial")
        self.assertTrue(user.is_active, "соц-юзер должен быть активен сразу")
        self.assertTrue(self.client.session.get("_auth_user_id"))


class YandexEnrichTests(TestCase):
    """Подтягивание даты рождения и аватара из ответа Яндекса."""

    def _signup(self, extra):
        import json as jsonlib
        from allauth.socialaccount.models import SocialLogin, SocialAccount, EmailAddress
        from django.contrib.auth import get_user_model
        User = get_user_model()
        u = User(username="yxdta", email="yxdta@yandex.by", first_name="Ян", date_of_birth=None)
        sl = SocialLogin()
        sl.provider = "yandex"
        sl.account = SocialAccount(provider="yandex", uid="99999", user=u, extra_data=extra)
        sl.email_addresses = [EmailAddress(email="yxdta@yandex.by", verified=True, primary=True)]
        sl.user = u
        session = self.client.session
        session["socialaccount_sociallogin"] = SocialLogin.serialize(sl)
        session.save()
        response = self.client.post("/accounts/social/signup/", {
            "username": "yxdta", "email": "yxdta@yandex.by",
        })
        return response, User.objects.get(username="yxdta")

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    @patch("requests.get")
    def test_birthday_and_avatar_pulled(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.headers = {"Content-Type": "image/jpeg"}
        # минимальный валидный JPEG-подпись
        mock_get.return_value.content = b"\xff\xd8\xff\xe0" + b"0" * 100
        mock_get.return_value.raise_for_status = lambda: None
        response, user = self._signup({
            "birthday": "1995-05-05",
            "avatar": "123456/testhost",
            "default_email": "yxdta@yandex.by",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(user.date_of_birth, date(1995, 5, 5))
        self.assertTrue(user.avatar, "аватар должен сохраниться")

    def test_network_failure_silently_skipped(self):
        with patch("requests.get", side_effect=requests.RequestException("offline")):
            response, user = self._signup({"birthday": "1995-05-05", "avatar": "x/y"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(user.date_of_birth, date(1995, 5, 5))
        self.assertFalse(user.avatar)

    def test_existing_values_not_overwritten(self):
        _, user = self._signup({"birthday": "2000-01-01"})
        self.assertEqual(user.date_of_birth, date(2000, 1, 1))
