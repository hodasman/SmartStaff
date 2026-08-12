from django.db import migrations
from django.utils.text import slugify


def _normalize_protocols(text):
    if not text:
        return []
    # split on comma, slash, semicolon, or ' and '
    parts = [p.strip() for p in __import__('re').split(r',|/|;|\band\b|&', text) if p.strip()]
    result = []
    for p in parts:
        low = p.lower()
        if 'wifi' in low or 'wi-fi' in low or 'wi fi' in low:
            result.append('Wi‑Fi')
        elif 'zigbee' in low:
            result.append('Zigbee')
        elif 'z-wave' in low or 'zwave' in low or 'z wave' in low:
            result.append('Z-Wave')
        elif 'bluetooth' in low:
            result.append('Bluetooth')
        elif 'thread' in low:
            result.append('Thread')
        elif low.strip() in ('rf', 'radio'):
            result.append('RF')
        elif 'ir' in low:
            result.append('IR')
        else:
            # fallback: title-case the token
            result.append(p.title())
    # dedupe while preserving order
    seen = set()
    out = []
    for x in result:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def forwards(apps, schema_editor):
    Device = apps.get_model('mainapp', 'Device')
    Protocol = apps.get_model('mainapp', 'Protocol')
    db_alias = schema_editor.connection.alias
    for device in Device.objects.using(db_alias).all():
        # old field `protocol` still exists in DB at this migration
        old = getattr(device, 'protocol', None)
        if not old:
            continue
        names = _normalize_protocols(old)
        for name in names:
            slug = slugify(name)
            proto, _ = Protocol.objects.using(db_alias).get_or_create(title=name, defaults={'slug': slug})
            device.protocols.add(proto)


def reverse(apps, schema_editor):
    # no-op reverse: leave devices untouched
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("mainapp", "0025_create_protocol_and_add_field"),
    ]

    operations = [
        migrations.RunPython(forwards, reverse),
    ]
