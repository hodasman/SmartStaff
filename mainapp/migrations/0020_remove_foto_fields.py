from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0019_create_deviceimage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='device',
            name='foto1',
        ),
        migrations.RemoveField(
            model_name='device',
            name='foto2',
        ),
        migrations.RemoveField(
            model_name='device',
            name='foto3',
        ),
        migrations.RemoveField(
            model_name='device',
            name='foto4',
        ),
    ]
