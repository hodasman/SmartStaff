from django import forms

from mainapp.models import Rating, RatingStar


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

    