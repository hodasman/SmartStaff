from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("mainapp", "0023_alter_device_set"),
    ]

    operations = [
        migrations.RenameField(
            model_name="device",
            old_name="set",
            new_name="package_contents",
        ),
    ]
