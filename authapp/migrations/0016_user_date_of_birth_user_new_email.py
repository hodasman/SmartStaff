from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authapp", "0015_alter_user_age_alter_user_avatar_and_more"),
    ]

    operations = [
        # age (int) -> date_of_birth (date): типы несовместимы, значение
        # возраста не конвертируется в дату автоматически -> данные age
        # не переносятся (поле опциональное)
        migrations.RemoveField(
            model_name="user",
            name="age",
        ),
        migrations.AddField(
            model_name="user",
            name="date_of_birth",
            field=models.DateField(blank=True, null=True, verbose_name="date of birth"),
        ),
        migrations.AddField(
            model_name="user",
            name="new_email",
            field=models.EmailField(blank=True, null=True, verbose_name="new email"),
        ),
    ]
