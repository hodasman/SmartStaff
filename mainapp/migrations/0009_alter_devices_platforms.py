# Generated by Django 4.2.8 on 2024-02-06 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0008_remove_scenarios_images_scenarios_img_1_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devices',
            name='platforms',
            field=models.ManyToManyField(blank=True, to='mainapp.platforms', verbose_name='Платформы'),
        ),
    ]