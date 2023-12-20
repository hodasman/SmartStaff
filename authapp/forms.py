from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UsernameField


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
        "password1",
        "password2",
        "email",
        "first_name",
        "last_name",
    ]

    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
        )
        field_classes = {"username": UsernameField}
