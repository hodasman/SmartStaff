from django.db import migrations, models


def move_devices_to_device_types(apps, schema_editor):
    """Перенести типы устройств из старого поля devices в новое device_types."""
    Scenario = apps.get_model("mainapp", "Scenario")

    for scenario in Scenario.objects.all().iterator():
        type_ids = set(
            scenario.devices.values_list("device_type_id", flat=True)
        )
        type_ids.discard(None)

        if type_ids:
            scenario.device_types.add(*type_ids)


class Migration(migrations.Migration):

    dependencies = [
        ("mainapp", "0035_remove_requireddevice_device_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="scenario",
            name="device_types",
            field=models.ManyToManyField(
                related_name="scenarios",
                to="mainapp.devicetype",
                verbose_name="Device types",
            ),
        ),
        migrations.RunPython(
            move_devices_to_device_types,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RemoveField(
            model_name="scenario",
            name="devices",
        ),
    ]
