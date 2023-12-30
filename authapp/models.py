from pathlib import Path
from time import time

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.validators import EmailValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


def users_avatars_path(instance, filename):
    # file will be uploaded to
    # MEDIA_ROOT / user_<username> / avatars / <filename>
    num = int(time() * 1000)
    suff = Path(filename).suffix
    return "user_{0}/avatars/{1}".format(instance.username, f"pic_{num}{suff}")


class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, username, first_name, age, email, password=None):
        """
        Creates and saves a User with the given first_name, email, phone_number and password.
        """
        if not email:
            raise ValueError("Необходимо задать адрес электронной почты")
        if not username:
            raise ValueError("Необходимо задать имя пользователя")

        user = self.model(
            username=username,
            first_name=first_name,
            age=age,
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.is_author = False
        user.save(using=self._db)
        return user

    def create_superuser(self, username, first_name, age, email, password=None):
        """
        Creates and saves a SuperUser with the given first_name, email, phone_number and password.
        """
        user = self.create_user(
            username=username,
            first_name=first_name,
            age=age,
            email=self.normalize_email(email),
            password=password,
        )
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.is_author = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username_validator = ASCIIUsernameValidator()
    username = models.CharField(
        _("Мянушка(login)"),
        max_length=15,
        unique=True,
        help_text=_("Максимальное значение 15 символов. Используйте только буквы, цифры или знаки +/-/_"),
        validators=[username_validator],
        error_messages={
            "unique": _("Такой пользователь уже существует"),
        },
    )
    first_name = models.CharField(_("Имя"), max_length=150, blank=True)
    age = models.PositiveIntegerField(_("Возраст"), blank=True, null=True)
    avatar = models.ImageField(upload_to=users_avatars_path, blank=True, null=True)
    email = models.EmailField(
        verbose_name="Адрес электронной почты",
        unique=True,
        blank=False,
        validators=[EmailValidator],
        error_messages={
            "unique": _("Пользователь с таким email уже существует!"),
        },
    )
    date_joined = models.DateTimeField(_("Дата создания"), auto_now_add=True)
    is_author = models.BooleanField(
        _("Статус автора"),
        default=False,
        help_text=_("Автор может добавлять статьи на сайт"),
    )
    is_staff = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "age"]

    def __str__(self):
        return f"{self.username}"
