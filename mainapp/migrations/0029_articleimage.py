from django.db import migrations, models
import django.db.models.deletion


def forwards_func(apps, schema_editor):
    Article = apps.get_model('mainapp', 'Article')
    ArticleImage = apps.get_model('mainapp', 'ArticleImage')
    for article in Article.objects.all():
        for i in range(1, 26):
            field_name = f'img_{i}'
            if hasattr(article, field_name):
                img = getattr(article, field_name)
                try:
                    if img:
                        # create ArticleImage with same file reference
                        ArticleImage.objects.create(
                            article_id=article.id,
                            image=img,
                            order=i,
                            is_main=(i == 1),
                        )
                except Exception:
                    # skip problematic files
                    continue


def reverse_func(apps, schema_editor):
    # reverse migration: try to move back first 25 images into img_1..img_25 if fields exist
    Article = apps.get_model('mainapp', 'Article')
    ArticleImage = apps.get_model('mainapp', 'ArticleImage')
    for article in Article.objects.all():
        imgs = ArticleImage.objects.filter(article_id=article.id).order_by('order', 'id')
        for img in imgs:
            field_name = f'img_{img.order}'
            if hasattr(article, field_name):
                try:
                    setattr(article, field_name, img.image)
                except Exception:
                    continue
        article.save()


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0028_rename_model_and_platforms'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=lambda instance, filename: instance.article.slug + '/' + filename, verbose_name='Image')),
                ('alt', models.CharField(blank=True, max_length=255, null=True, verbose_name='Alt text')),
                ('is_main', models.BooleanField(default=False, verbose_name='Main image')),
                ('order', models.PositiveSmallIntegerField(default=0, verbose_name='Order')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='mainapp.Article', verbose_name='Article')),
            ],
            options={
                'ordering': ['order', 'id'],
                'verbose_name': 'Article image',
                'verbose_name_plural': 'Article images',
            },
        ),
        migrations.RunPython(forwards_func, reverse_func),
        # remove old image fields if they still exist in model/state
        migrations.RemoveField(
            model_name='article',
            name='img_1',
        ),
        migrations.RemoveField(model_name='article', name='img_2'),
        migrations.RemoveField(model_name='article', name='img_3'),
        migrations.RemoveField(model_name='article', name='img_4'),
        migrations.RemoveField(model_name='article', name='img_5'),
        migrations.RemoveField(model_name='article', name='img_6'),
        migrations.RemoveField(model_name='article', name='img_7'),
        migrations.RemoveField(model_name='article', name='img_8'),
        migrations.RemoveField(model_name='article', name='img_9'),
        migrations.RemoveField(model_name='article', name='img_10'),
        migrations.RemoveField(model_name='article', name='img_11'),
        migrations.RemoveField(model_name='article', name='img_12'),
        migrations.RemoveField(model_name='article', name='img_13'),
        migrations.RemoveField(model_name='article', name='img_14'),
        migrations.RemoveField(model_name='article', name='img_15'),
        migrations.RemoveField(model_name='article', name='img_16'),
        migrations.RemoveField(model_name='article', name='img_17'),
        migrations.RemoveField(model_name='article', name='img_18'),
        migrations.RemoveField(model_name='article', name='img_19'),
        migrations.RemoveField(model_name='article', name='img_20'),
        migrations.RemoveField(model_name='article', name='img_21'),
        migrations.RemoveField(model_name='article', name='img_22'),
        migrations.RemoveField(model_name='article', name='img_23'),
        migrations.RemoveField(model_name='article', name='img_24'),
        migrations.RemoveField(model_name='article', name='img_25'),
    ]
