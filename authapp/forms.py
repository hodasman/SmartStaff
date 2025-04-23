import os

from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import (PasswordResetForm, SetPasswordForm,
                                       UserCreationForm, UsernameField)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class CreateUserForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = "Пароль"
        self.fields["password2"].label = "Праверка пороля"
        self.fields["country"].label = "Страна"
        
        self.fields[
            "password1"
        ].help_text = "Ваш пароль не должен быть слишком похож на другую вашу личную информацию.<br>\
            Ваш пароль должен содержать не менее 8 символов.<br>\
            Ваш пароль не может быть полностью числовым."
        self.fields["password2"].help_text = "Введите пароль повторно"
        
    
    field_order = [
        "username",
        "first_name",
        "last_name",
        "email",
        "password1",
        "password2",
        "avatar",
        "age",
    ]
    
    class Meta:
        model = get_user_model()
        fields = ("username", "email", "first_name", "last_name", "age", "country", "avatar")
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


class CustomPasswordResetForm(PasswordResetForm):  
    email = forms.EmailField(  
        label="Email",  
        max_length=254,  
        widget=forms.EmailInput(  
            attrs={'class': 'form-control',  
                   'placeholder': 'Введите Email',  
                   "autocomplete": "email"}  
        )  
    )  


class CustomSetPasswordForm(SetPasswordForm):  
    error_messages = {  
        "password_mismatch": "Пароли не совпадают"  
    }  
    new_password1 = forms.CharField(  
        label='Новый пароль',  
        widget=forms.PasswordInput(  
            attrs={'class': 'form-control',  
                   'placeholder': 'Введите новый пароль',  
                   "autocomplete": "new-password"}  
        ),  
        strip=False,  
        help_text=password_validation.password_validators_help_text_html(),  
    )  
    new_password2 = forms.CharField(  
        label='Подтверждение нового пароля',  
        strip=False,  
        widget=forms.PasswordInput(  
            attrs={'class': 'form-control',  
                   'placeholder': 'Подтвердите новый пароль',  
                   "autocomplete": "new-password"}  
        ),  
    )