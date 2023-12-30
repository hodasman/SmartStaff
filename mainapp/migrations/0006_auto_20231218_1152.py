# Generated by Django 3.2.22 on 2023-12-18 11:52

import autoslug.fields
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mainapp", "0005_auto_20231210_1837"),
    ]

    operations = [
        migrations.AddField(
            model_name="devices",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name="Создан"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="devices",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="Обновлен"),
        ),
        migrations.AlterField(
            model_name="articlecategory",
            name="slug",
            field=autoslug.fields.AutoSlugField(editable=False, populate_from="title"),
        ),
        migrations.AlterField(
            model_name="devicecategory",
            name="slug",
            field=autoslug.fields.AutoSlugField(editable=False, populate_from="title"),
        ),
    ]
