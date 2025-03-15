from django import forms

from .models import Subscribers


class SubscribeForm(forms.ModelForm):
    '''Форма подписки по email'''
    def clean_name(self):
        name = self.cleaned_data.get('email')

    class Meta:
        model = Subscribers
        fields = ("email",)
        widgets = {
            "email": forms.EmailInput(attrs={'placeholder': 'email'})
        }