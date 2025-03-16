from django import forms

from .models import Subscribers


class SubscribeForm(forms.ModelForm):
    '''Форма подписки по email'''
    def __init__(self, *args, **kwargs):
        super(SubscribeForm, self).__init__(*args, **kwargs)
        self.fields['email'].label = ""
        
    def clean_name(self):
        name = self.cleaned_data.get('email')

    class Meta:
        model = Subscribers
        fields = ("email",)
        widgets = {
            "email": forms.EmailInput(attrs={'placeholder': 'email'})
        }