from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.validators import EmailValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, username, first_name, last_name, email, password=None):
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
            last_name=last_name,
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.is_author = False
        user.save(using=self._db)
        return user

    def create_superuser(self, username, first_name, last_name, email, password=None):
        """
        Creates and saves a SuperUser with the given first_name, email, phone_number and password.
        """
        user = self.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
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
        _("username"),
        max_length=150,
        unique=True,
        help_text=_("Используйте только буквы, цифры или знаки @/./+/-/_"),
        validators=[username_validator],
        error_messages={
            "unique": _("Такой пользователь уже существует"),
        },
    )
    first_name = models.CharField(_("Имя"), max_length=150, blank=True)
    last_name = models.CharField(_("Фамилия"), max_length=150, blank=True)
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
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    def __str__(self):
        return f"{self.username} {self.email}"
