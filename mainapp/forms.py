from django import forms
from django.utils.translation import gettext_lazy as _

from mainapp.models import Feedback, Rating, RatingStar


class RaitingForm(forms.ModelForm):
    '''Форма добавления рейтинга. Выводит список всех добавленных вариантов оценок (1-5) 
    которые у нас храняться в отдельной таблице в базе ratingstar. Эту форму передаем во
    вьюс детальной траницы сценария ScenariosDetailView в качестве контента. Чтобы в шаблоне
    в цикле for вывести все звезды.
    '''
    star = forms.ModelChoiceField(
        queryset=RatingStar.objects.all(), widget=forms.RadioSelect(), empty_label=None
    )

    class Meta:
        model = Rating
        fields = ('star',)


class CommentForm(forms.Form):
 
    comment_area = forms.CharField(
        label="",
        widget=forms.Textarea(attrs={'placeholder': _('Your message')}),
        
    )


class FeedbackCreateForm(forms.ModelForm):
    """
    Форма отправки обратной связи
    """
    def __init__(self, *args, **kwargs):
        super(FeedbackCreateForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].label =""

    class Meta:
        model = Feedback
        fields = ('content', 'name', 'email', 'subject',)
        widgets={
            'content': forms.Textarea(attrs={'class': 'col-12 form-group form-control w-100',
                                              'placeholder':  _('Enter your message'),
                                              'autocomplete': 'off', 'cols': "30", 'rows':"9",
                                              'onfocus': "this.placeholder = ''", 
                                              'onblur':"this.placeholder = 'Enter your message text'"}), 
            'name': forms.TextInput(attrs={'class': 'col-sm-6 form-group form-control',
                                              'placeholder':  _('Enter your name'),
                                              'autocomplete': 'off', 'onfocus': "this.placeholder = ''", 
                                              'onblur':"this.placeholder = 'Enter your name'"}),
            'email': forms.EmailInput(attrs={'class': 'col-sm-6 form-group form-control',
                                              'placeholder':  _('Enter your email'),
                                              'autocomplete': 'off', 'onfocus': "this.placeholder = ''", 
                                              'onblur':"this.placeholder = 'Enter your email'"}),
            'subject': forms.TextInput(attrs={'class': 'col-12 form-group form-control',
                                              'placeholder':  _('Enter subject'),
                                              'autocomplete': 'off', 'onfocus': "this.placeholder = ''", 
                                              'onblur':"this.placeholder = 'Enter subject'"}),
        }
