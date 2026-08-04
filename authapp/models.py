from pathlib import Path
from time import time

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.mail import send_mail
from django.core.validators import EmailValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from mainapp.models import Device


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
            raise ValueError("You must specify an email address")
        if not username:
            raise ValueError("Username required")

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
        _("username"),
        max_length=15,
        unique=True,
        help_text=_("Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only"),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_("first name"), max_length=20, blank=True)
    last_name = models.CharField(_("last name"), max_length=20, blank=True, null=True)
    age = models.PositiveIntegerField(_("age"), blank=True, null=True)
    avatar = models.ImageField(_("avatar"), upload_to=users_avatars_path, blank=True, null=True)
    country = CountryField(blank=True, null=True)
    email = models.EmailField(
        verbose_name="email address",
        unique=True,
        blank=False,
        validators=[EmailValidator],
        error_messages={
            "unique": _("A user with that email address already exists."),
        },
    )
    date_joined = models.DateTimeField(_("Date of creation"), auto_now_add=True)
    is_author = models.BooleanField(
        _("author status"),
        default=False,
        help_text=_("The author can add articles to the site"),
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    objects = UserManager()
    devices = models.ManyToManyField(Device, verbose_name="devices", blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "age",]

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        return f"{self.username}"
