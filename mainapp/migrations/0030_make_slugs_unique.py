from django.db import migrations


def make_unique_slugs(apps, schema_editor):
    Article = apps.get_model('mainapp', 'Article')
    ArticleCategory = apps.get_model('mainapp', 'ArticleCategory')

    # Ensure unique slugs for ArticleCategory
    seen = {}
    for cat in ArticleCategory.objects.all():
        slug = cat.slug or ''
        if slug in seen:
            new_slug = f"{slug}-{cat.id}"
            cat.slug = new_slug
            cat.save(update_fields=['slug'])
        else:
            seen[slug] = cat.id

    # Ensure unique slugs for Article
    seen = {}
    for art in Article.objects.all():
        slug = art.slug or ''
        if slug in seen:
            new_slug = f"{slug}-{art.id}"
            art.slug = new_slug
            art.save(update_fields=['slug'])
        else:
            seen[slug] = art.id


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0029_articleimage'),
    ]

    operations = [
        migrations.RunPython(make_unique_slugs, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='articlecategory',
            name='slug',
            field=__import__('autoslug').autoslug.AutoSlugField(populate_from='title', unique=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='slug',
            field=__import__('autoslug').autoslug.AutoSlugField(populate_from='title', verbose_name='URL', unique=True),
        ),
    ]
