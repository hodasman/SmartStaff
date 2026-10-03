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
        self.fields["password1"].label = _("Password")
        self.fields["password2"].label = _("Password verification")
        self.fields["country"].label = _("Country")
        self.fields["date_of_birth"].widget = forms.DateInput(
            attrs={"type": "date"}, format="%Y-%m-%d"
        )
        self.fields["date_of_birth"].label = _("Date of birth")
        
    
    field_order = [
        "username",
        "first_name",
        "last_name",
        "email",
        "password1",
        "password2",
        "avatar",
        "date_of_birth",
    ]
    
    class Meta:
        model = get_user_model()
        fields = ("username", "email", "first_name", "last_name", "date_of_birth", "country", "avatar")
        field_classes = {"username": UsernameField}
        


class UserChangeForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "email",
            "first_name",
            "date_of_birth",
            "avatar",
        )
        field_classes = {"username": UsernameField}
        widgets = {"date_of_birth": forms.DateInput(attrs={"type": "date"})}

    def clean_avatar(self):
        arg_as_str = "avatar"
        if arg_as_str in self.changed_data and self.instance.avatar:
            if os.path.exists(self.instance.avatar.path):
                os.remove(self.instance.avatar.path)
        return self.cleaned_data.get(arg_as_str)

    def clean_date_of_birth(self):
        data = self.cleaned_data.get("date_of_birth")
        if data:
            from datetime import date
            today = date.today()
            if data > today:
                raise ValidationError(_("Date of birth cannot be in the future."))
            if data.year < 1900:
                raise ValidationError(_("Write your date of birth correctly."))
        return data


class ResendActivationForm(forms.Form):
    """Повторная отправка письма активации для неактивированного аккаунта."""
    email = forms.EmailField(  
        label="Email",  
        max_length=254,  
        widget=forms.EmailInput(  
            attrs={
                "class": "form-control",
                "placeholder": _("Enter Email"),
                "autocomplete": "email",
            }
        ),
    )  

    def get_user(self):
        User = get_user_model()
        try:
            return User.objects.get(
                email__iexact=self.cleaned_data["email"], is_active=False
            )
        except User.DoesNotExist:
            return None


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(
            attrs={'class': 'form-control',  
                   'placeholder': _('Enter Email'),
                   "autocomplete": "email"}
        )
    )


class CustomSetPasswordForm(SetPasswordForm):
    error_messages = {
        "password_mismatch": _("The passwords do not match")
    }
    new_password1 = forms.CharField(
        label=_('New password'),
        widget=forms.PasswordInput(
            attrs={'class': 'form-control',
                   'placeholder': _('Enter new password'),
                   "autocomplete": "new-password"}
        ),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_('Confirm new password'),
        strip=False,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control',
                   'placeholder': _('Confirm new password'),
                   "autocomplete": "new-password"}
        ),
    )
