from django.db import migrations, models

import mainapp.models


def forwards(apps, schema_editor):
    Scenario = apps.get_model('mainapp', 'Scenario')
    ScenarioImage = apps.get_model('mainapp', 'ScenarioImage')
    for s in Scenario.objects.all():
        order = 0
        # migrate img_1..img_24
        for i in range(1, 25):
            field = f'img_{i}'
            try:
                img = getattr(s, field)
            except Exception:
                img = None
            if img:
                ScenarioImage.objects.create(scenario_id=s.pk, image=img, order=order)
                order += 1
        # migrate scheme
        try:
            scheme = getattr(s, 'scheme')
        except Exception:
            scheme = None
        if scheme:
            ScenarioImage.objects.create(scenario_id=s.pk, image=scheme, order=order)
            order += 1


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0031_add_indexes'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScenarioImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=mainapp.models.scenarios_img_path, verbose_name='Image')),
                ('alt', models.CharField(blank=True, max_length=255, null=True, verbose_name='Alt text')),
                ('is_main', models.BooleanField(default=False, verbose_name='Main image')),
                ('order', models.PositiveSmallIntegerField(default=0, verbose_name='Order')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('scenario', models.ForeignKey(on_delete=models.CASCADE, related_name='images', to='mainapp.scenario', verbose_name='Scenario')),
            ],
            options={
                'ordering': ['order', 'id'],
                'verbose_name': 'Scenario image',
                'verbose_name_plural': 'Scenario images',
            },
        ),
        migrations.RunPython(forwards, migrations.RunPython.noop),
        # remove old image fields
        migrations.RemoveField(
            model_name='scenario',
            name='img_1',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='img_2',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='img_3',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='img_4',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='img_5',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='img_6',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='img_7',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='img_8',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='img_9',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='img_10',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='img_11',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='img_12',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='img_13',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='img_14',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='img_15',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='img_16',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='img_17',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='img_18',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='img_19',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='img_20',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='img_21',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='img_22',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='img_23',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='img_24',
        ),
        migrations.RemoveField(
            model_name='scenario',
            name='scheme',
        ),
    ]
