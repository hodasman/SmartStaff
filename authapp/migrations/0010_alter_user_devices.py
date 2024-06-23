# Generated by Django 4.2.8 on 2024-05-21 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0014_idea_remove_scenario_img_25_scenario_platform_and_more'),
        ('authapp', '0009_user_devices'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='devices',
            field=models.ManyToManyField(blank=True, to='mainapp.device', verbose_name='Устройства'),
        ),
    ]