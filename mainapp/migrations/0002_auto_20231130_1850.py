# Generated by Django 3.2.22 on 2023-11-30 18:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import mainapp.models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("mainapp", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="devices",
            name="foto",
        ),
        migrations.AddField(
            model_name="articles",
            name="author",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Автор",
            ),
        ),
        migrations.AddField(
            model_name="devices",
            name="author",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Автор",
            ),
        ),
        migrations.AddField(
            model_name="devices",
            name="foto1",
            field=models.ImageField(
                blank=True, null=True, upload_to=mainapp.models.device_foto_path, verbose_name="Фото устройства_1"
            ),
        ),
        migrations.AddField(
            model_name="scenarios",
            name="author",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Автор",
            ),
        ),
    ]