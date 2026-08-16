from django.db import migrations
from autoslug import AutoSlugField
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0030_make_slugs_unique'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articlecategory',
            name='slug',
            field=AutoSlugField(populate_from='title', unique=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='slug',
            field=AutoSlugField(populate_from='title', verbose_name='URL', unique=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='title',
            field=models.CharField(max_length=256, verbose_name='Name', db_index=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created', editable=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='deleted',
            field=models.BooleanField(default=False, db_index=True),
        ),
    ]
