from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("mainapp", "0027_remove_old_protocol_field"),
    ]

    operations = [
        migrations.RenameField(
            model_name='device',
            old_name='model',
            new_name='model_name',
        ),
        migrations.RenameField(
            model_name='device',
            old_name='platforms',
            new_name='ecosystem',
        ),
    ]
