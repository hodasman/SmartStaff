from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mainapp", "0024_rename_set_to_package_contents"),
    ]

    operations = [
        migrations.CreateModel(
            name="Protocol",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ("title", models.CharField(max_length=64, verbose_name='Name')),
                ("slug", models.SlugField(blank=True, max_length=100, null=True)),
            ],
            options={"verbose_name": "Protocol", "verbose_name_plural": "Protocols", "ordering": ["title"]},
        ),
        migrations.AddField(
            model_name="device",
            name="protocols",
            field=models.ManyToManyField(blank=True, related_name="devices", to="mainapp.Protocol", verbose_name='Supported protocols'),
        ),
    ]
