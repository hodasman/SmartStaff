from django import forms

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
        widget=forms.Textarea(attrs={'placeholder': 'Ваше сообщение'}),
        
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
                                              'placeholder':  'Увядзіце тэкст паведамлення',
                                              'autocomplete': 'off', 'cols': "30", 'rows':"9",
                                              'onfocus': "this.placeholder = ''", 
                                              'onblur':"this.placeholder = 'Увядзіце тэкст паведамлення'"}), 
            'name': forms.TextInput(attrs={'class': 'col-sm-6 form-group form-control',
                                              'placeholder':  'Увядзіце свае імя',
                                              'autocomplete': 'off', 'onfocus': "this.placeholder = ''", 
                                              'onblur':"this.placeholder = 'Увядзіце свае імя'"}),
            'email': forms.EmailInput(attrs={'class': 'col-sm-6 form-group form-control',
                                              'placeholder':  'Увядзіце свой email',
                                              'autocomplete': 'off', 'onfocus': "this.placeholder = ''", 
                                              'onblur':"this.placeholder = 'Увядзіце свой email'"}),
            'subject': forms.TextInput(attrs={'class': 'col-12 form-group form-control',
                                              'placeholder':  'Тэма зварота',
                                              'autocomplete': 'off', 'onfocus': "this.placeholder = ''", 
                                              'onblur':"this.placeholder = 'Тэма зварота'"}),
        }
