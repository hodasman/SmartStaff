# Generated by Django 4.2.8 on 2024-02-24 17:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0011_scenariocomment_articlecomment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='articlecomment',
            old_name='article_id',
            new_name='article',
        ),
        migrations.RenameField(
            model_name='articlecomment',
            old_name='author_id',
            new_name='author',
        ),
        migrations.RenameField(
            model_name='scenariocomment',
            old_name='author_id',
            new_name='author',
        ),
        migrations.RenameField(
            model_name='scenariocomment',
            old_name='article_id',
            new_name='scenario',
        ),
    ]