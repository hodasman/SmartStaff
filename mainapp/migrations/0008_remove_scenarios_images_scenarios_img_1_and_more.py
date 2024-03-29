# Generated by Django 4.2.8 on 2024-01-11 18:21

import autoslug.fields
from django.db import migrations, models

import mainapp.models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0007_remove_articles_images_articles_img_1_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scenarios',
            name='images',
        ),
        migrations.AddField(
            model_name='scenarios',
            name='img_1',
            field=models.ImageField(blank=True, null=True, upload_to=mainapp.models.scenarios_img_path, verbose_name='Картинка_1'),
        ),
        migrations.AddField(
            model_name='scenarios',
            name='img_10',
            field=models.ImageField(blank=True, null=True, upload_to=mainapp.models.scenarios_img_path, verbose_name='Картинка_10'),
        ),
        migrations.AddField(
            model_name='scenarios',
            name='img_11',
            field=models.ImageField(blank=True, null=True, upload_to=mainapp.models.scenarios_img_path, verbose_name='Картинка_11'),
        ),
        migrations.AddField(
            model_name='scenarios',
            name='img_12',
            field=models.ImageField(blank=True, null=True, upload_to=mainapp.models.scenarios_img_path, verbose_name='Картинка_12'),
        ),
        migrations.AddField(
            model_name='scenarios',
            name='img_13',
            field=models.ImageField(blank=True, null=True, upload_to=mainapp.models.scenarios_img_path, verbose_name='Картинка_13'),
        ),
        migrations.AddField(
            model_name='scenarios',
            name='img_14',
            field=models.ImageField(blank=True, null=True, upload_to=mainapp.models.scenarios_img_path, verbose_name='Картинка_14'),
        ),
        migrations.AddField(
            model_name='scenarios',
            name='img_15',
            field=models.ImageField(blank=True, null=True, upload_to=mainapp.models.scenarios_img_path, verbose_name='Картинка_15'),
        ),
        migrations.AddField(
            model_name='scenarios',
            name='img_16',
            field=models.ImageField(blank=True, null=True, upload_to=mainapp.models.scenarios_img_path, verbose_name='Картинка_16'),
        ),
        migrations.AddField(
            model_name='scenarios',
            name='img_17',
            field=models.ImageField(blank=True, null=True, upload_to=mainapp.models.scenarios_img_path, verbose_name='Картинка_17'),
        ),
        migrations.AddField(
            model_name='scenarios',
            name='img_18',
            field=models.ImageField(blank=True, null=True, upload_to=mainapp.models.scenarios_img_path, verbose_name='Картинка_18'),
        ),
        migrations.AddField(
            model_name='scenarios',
            name='img_19',
            field=models.ImageField(blank=True, null=True, upload_to=mainapp.models.scenarios_img_path, verbose_name='Картинка_19'),
        ),
        migrations.AddField(
            model_name='scenarios',
            name='img_2',
            field=models.ImageField(blank=True, null=True, upload_to=mainapp.models.scenarios_img_path, verbose_name='Картинка_2'),
        ),
        migrations.AddField(
            model_name='scenarios',
            name='img_20',
            field=models.ImageField(blank=True, null=True, upload_to=mainapp.models.scenarios_img_path, verbose_name='Картинка_20'),
        ),
        migrations.AddField(
            model_name='scenarios',
            name='img_21',
            field=models.ImageField(blank=True, null=True, upload_to=mainapp.models.scenarios_img_path, verbose_name='Картинка_21'),
        ),
        migrations.AddField(
            model_name='scenarios',
            name='img_22',
            field=models.ImageField(blank=True, null=True, upload_to=mainapp.models.scenarios_img_path, verbose_name='Картинка_22'),
        ),
        migrations.AddField(
            model_name='scenarios',
            name='img_23',
            field=models.ImageField(blank=True, null=True, upload_to=mainapp.models.scenarios_img_path, verbose_name='Картинка_23'),
        ),
        migrations.AddField(
            model_name='scenarios',
            name='img_24',
            field=models.ImageField(blank=True, null=True, upload_to=mainapp.models.scenarios_img_path, verbose_name='Картинка_24'),
        ),
        migrations.AddField(
            model_name='scenarios',
            name='img_25',
            field=models.ImageField(blank=True, null=True, upload_to=mainapp.models.scenarios_img_path, verbose_name='Картинка_25'),
        ),
        migrations.AddField(
            model_name='scenarios',
            name='img_3',
            field=models.ImageField(blank=True, null=True, upload_to=mainapp.models.scenarios_img_path, verbose_name='Картинка_3'),
        ),
        migrations.AddField(
            model_name='scenarios',
            name='img_4',
            field=models.ImageField(blank=True, null=True, upload_to=mainapp.models.scenarios_img_path, verbose_name='Картинка_4'),
        ),
        migrations.AddField(
            model_name='scenarios',
            name='img_5',
            field=models.ImageField(blank=True, null=True, upload_to=mainapp.models.scenarios_img_path, verbose_name='Картинка_5'),
        ),
        migrations.AddField(
            model_name='scenarios',
            name='img_6',
            field=models.ImageField(blank=True, null=True, upload_to=mainapp.models.scenarios_img_path, verbose_name='Картинка_6'),
        ),
        migrations.AddField(
            model_name='scenarios',
            name='img_7',
            field=models.ImageField(blank=True, null=True, upload_to=mainapp.models.scenarios_img_path, verbose_name='Картинка_7'),
        ),
        migrations.AddField(
            model_name='scenarios',
            name='img_8',
            field=models.ImageField(blank=True, null=True, upload_to=mainapp.models.scenarios_img_path, verbose_name='Картинка_8'),
        ),
        migrations.AddField(
            model_name='scenarios',
            name='img_9',
            field=models.ImageField(blank=True, null=True, upload_to=mainapp.models.scenarios_img_path, verbose_name='Картинка_9'),
        ),
        migrations.AddField(
            model_name='scenarios',
            name='main_img',
            field=models.ImageField(blank=True, null=True, upload_to=mainapp.models.scenarios_img_path, verbose_name='Заглавная картинка'),
        ),
        migrations.AddField(
            model_name='scenarios',
            name='slug',
            field=autoslug.fields.AutoSlugField(default=2, editable=False, populate_from='title', verbose_name='URL'),
            preserve_default=False,
        ),
    ]
