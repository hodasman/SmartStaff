# Generated by Django 4.2.8 on 2024-05-21 17:35

import django.db.models.deletion
from django.db import migrations, models

import mainapp.models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0013_rename_articles_article_rename_devices_device_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Idea',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256, verbose_name='Название')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
            ],
            options={
                'verbose_name': 'Идея',
                'verbose_name_plural': 'Идеи',
                'ordering': ['title'],
            },
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='img_25',
        ),
        migrations.AddField(
            model_name='scenario',
            name='platform',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.platform'),
        ),
        migrations.AddField(
            model_name='scenario',
            name='scheme',
            field=models.ImageField(blank=True, null=True, upload_to=mainapp.models.scenarios_img_path, verbose_name='Схема'),
        ),
        migrations.AddField(
            model_name='scenario',
            name='idea',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.idea'),
        ),
    ]
