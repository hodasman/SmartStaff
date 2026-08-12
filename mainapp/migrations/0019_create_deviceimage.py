from django.db import migrations, models


def copy_images(apps, schema_editor):
    Device = apps.get_model('mainapp', 'Device')
    DeviceImage = apps.get_model('mainapp', 'DeviceImage')
    for device in Device.objects.all():
        order = 0
        for field in ('foto1', 'foto2', 'foto3', 'foto4'):
            try:
                f = getattr(device, field)
            except Exception:
                f = None
            if f:
                # f is a FieldFile; use its name (path) for ImageField
                DeviceImage.objects.create(device_id=device.id, image=f.name or f, order=order, is_main=(order == 0))
                order += 1


def reverse_copy(apps, schema_editor):
    # noop: keep backward migration simple
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0018_alter_device_device_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='devices_foto/', verbose_name='Image')),
                ('alt', models.CharField(blank=True, max_length=255, null=True, verbose_name='Alt text')),
                ('is_main', models.BooleanField(default=False, verbose_name='Main image')),
                ('order', models.PositiveSmallIntegerField(default=0, verbose_name='Order')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('device', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='images', to='mainapp.Device')),
            ],
            options={
                'verbose_name': 'Device image',
                'verbose_name_plural': 'Device images',
                'ordering': ['order', 'id'],
            },
        ),
        migrations.RunPython(copy_images, reverse_copy),
    ]
