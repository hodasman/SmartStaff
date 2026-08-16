from django import template

register = template.Library()

# Simple mapping keywords -> FontAwesome classes
ICON_MAP = {
    'light': 'fa-lightbulb',
    'lamp': 'fa-lightbulb',
    'bulb': 'fa-lightbulb',
    'лампа': 'fa-lightbulb',
    'лампочка': 'fa-lightbulb',
    'освещение': 'fa-lightbulb',
    'plug': 'fa-plug',
    'socket': 'fa-plug',
    'розетка': 'fa-plug',
    'sensor': 'fa-thermometer-half',
    'thermo': 'fa-thermometer-half',
    'датчик': 'fa-thermometer-half',
    'camera': 'fa-camera',
    'камера': 'fa-camera',
    'hub': 'fa-network-wired',
    'хаб': 'fa-network-wired',
    'безопасность': 'fa-lock',
    'бытовая техника': 'fa-home',
    'вода': 'fa-water',
    'сад': 'fa-leaf',
    'транспорт': 'fa-car',
    'убор': 'fa-broom',
    'шторы': 'fa-window-restore',
    'жалюзи': 'fa-window-restore',
    'энерг': 'fa-bolt',
    'электрик': 'fa-bolt',
    'мультимедиа': 'fa-tv',
    'колон': 'fa-volume-up',
    'робот': 'fa-robot',
    'пульт': 'fa-tv',
    'wifi': 'fa-wifi',
    'tv': 'fa-tv',
    'телевизор': 'fa-tv',
    'mobile': 'fa-mobile',
    'phone': 'fa-mobile',
    'телефон': 'fa-mobile',
    'pc': 'fa-desktop',
    'computer': 'fa-desktop',
    'компьютер': 'fa-desktop',
    'lock': 'fa-lock',
    'замок': 'fa-lock',
    'default': 'fa-microchip',
}


@register.filter(name='get_icon')
def get_icon(value):
    """Return a FontAwesome class based on the category/device type string.

    Matches keywords inside the provided value (case-insensitive).
    """
    if not value:
        return ICON_MAP['default']

    # If value is a model instance, try common display fields
    if hasattr(value, 'title') and value.title:
        s = str(value.title).lower()
    elif hasattr(value, 'name') and value.name:
        s = str(value.name).lower()
    else:
        s = str(value).lower()
    for key, cls in ICON_MAP.items():
        if key == 'default':
            continue
        if key in s:
            return cls
    return ICON_MAP['default']
