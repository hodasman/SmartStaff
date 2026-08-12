from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mainapp", "0022_alter_deviceimage_device_alter_deviceimage_id_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="device",
            name="set",
            field=models.TextField(verbose_name="Package contents"),
        ),
    ]
