import os

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class CreateUserForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = "Пароль"
        self.fields["password2"].label = "Праверка пороля"

        self.fields[
            "password1"
        ].help_text = "Ваш пароль не должен быть слишком похож на другую вашу личную информацию.<br>\
            Ваш пароль должен содержать не менее 8 символов.<br>\
            Ваш пароль не может быть полностью числовым."
        self.fields["password2"].help_text = "Введите пароль повторно"

    field_order = [
        "username",
        "email",
        "password1",
        "password2",
        "avatar" "first_name",
        "age",
    ]

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "first_name", "age", "avatar")
        field_classes = {"username": UsernameField}


class UserChangeForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "email",
            "first_name",
            "age",
            "avatar",
        )
        field_classes = {"username": UsernameField}

    def clean_avatar(self):
        arg_as_str = "avatar"
        if arg_as_str in self.changed_data and self.instance.avatar:
            if os.path.exists(self.instance.avatar.path):
                os.remove(self.instance.avatar.path)
        return self.cleaned_data.get(arg_as_str)

    def clean_age(self):
        data = self.cleaned_data.get("age")
        if data:
            if data < 10 or data > 100:
                raise ValidationError(_("Напішыце свой узрост правільна"))
        return data
