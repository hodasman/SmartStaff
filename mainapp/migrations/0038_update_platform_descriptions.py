from django.db import migrations


DESCRIPTIONS = {
    "Tuya (Smart Life)": (
        "Экосистема для умных устройств разных производителей, совместимых "
        "с Tuya и Smart Life. Подходит, если у вас уже есть такие устройства; "
        "доступность функций зависит от модели и способа подключения.",
        {"", None},
    ),
    "Apple Home (HomeKit)": (
        "Умный дом от Apple. Стоит рассмотреть, если у вас есть устройства "
        "этой компании. Для полноценной удалённой работы и автоматизаций "
        "нужен Apple TV 4-го поколения или новее либо колонка HomePod — "
        "они служат домашним хабом.",
        {"", None, "Умный дом от Apple"},
    ),
    "Mi Home (Xiaomi)": (
        "Экосистема Xiaomi для управления устройствами Mi и совместимыми "
        "устройствами. Подходит, если у вас уже есть техника Xiaomi; для "
        "некоторых датчиков и автоматизаций может понадобиться шлюз.",
        {"", None},
    ),
    "Yandex Alice": (
        "Умный дом с Алисой от Яндекса. Подходит, если вы пользуетесь "
        "устройствами с поддержкой Алисы; для голосового управления нужна "
        "колонка с Алисой, а некоторым устройствам требуется совместимый хаб.",
        {"", None, "Умный дом с Алисой"},
    ),
    "Aqara Home": (
        "Экосистема умного дома Aqara. Подходит для устройств Aqara и "
        "совместимых аксессуаров; для подключения многих датчиков и настройки "
        "автоматизаций нужен хаб Aqara.",
        {"", None},
    ),
}

PREVIOUS_DESCRIPTIONS = {
    "Tuya (Smart Life)": "",
    "Apple Home (HomeKit)": "Умный дом от Apple",
    "Mi Home (Xiaomi)": "",
    "Yandex Alice": "Умный дом с Алисой",
    "Aqara Home": "",
}


def populate_platform_descriptions(apps, schema_editor):
    Platform = apps.get_model("mainapp", "Platform")
    for title, (description, previous_values) in DESCRIPTIONS.items():
        platforms = Platform.objects.filter(title=title)
        for platform in platforms:
            if platform.description in previous_values:
                platform.description = description
                platform.save(update_fields=["description"])


def restore_platform_descriptions(apps, schema_editor):
    Platform = apps.get_model("mainapp", "Platform")
    for title, (description, _) in DESCRIPTIONS.items():
        Platform.objects.filter(
            title=title,
            description=description,
        ).update(description=PREVIOUS_DESCRIPTIONS[title])


class Migration(migrations.Migration):
    dependencies = [
        ("mainapp", "0037_device_is_legacy"),
    ]

    operations = [
        migrations.RunPython(
            populate_platform_descriptions,
            restore_platform_descriptions,
        ),
    ]
