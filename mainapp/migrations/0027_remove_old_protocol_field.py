from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("mainapp", "0026_populate_protocols"),
    ]

    operations = [
        migrations.RemoveField(
            model_name='device',
            name='protocol',
        ),
    ]
