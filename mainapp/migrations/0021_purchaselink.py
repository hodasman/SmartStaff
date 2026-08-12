from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0020_remove_foto_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='PurchaseLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marketplace', models.CharField(choices=[('ozon', 'Ozon'), ('wb', 'Wildberries'), ('aliexpress', 'AliExpress'), ('other', 'Other')], max_length=32, verbose_name='Marketplace')),
                ('url', models.URLField(verbose_name='URL')),
                ('affiliate', models.BooleanField(default=False, verbose_name='Affiliate')),
                ('note', models.CharField(blank=True, max_length=255, null=True, verbose_name='Note')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('device', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='purchase_links', to='mainapp.device')),
            ],
            options={'verbose_name': 'Purchase link', 'verbose_name_plural': 'Purchase links', 'ordering': ['-created_at']},
        ),
        migrations.RemoveField(
            model_name='device',
            name='link_to_buy',
        ),
    ]
