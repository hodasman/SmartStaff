from django import template

register = template.Library()

# Simple mapping keywords -> FontAwesome classes
ICON_MAP = {
    'light': 'fa-lightbulb',
    'lamp': 'fa-lightbulb',
    'bulb': 'fa-lightbulb',
    'plug': 'fa-plug',
    'socket': 'fa-plug',
    'sensor': 'fa-thermometer-half',
    'thermo': 'fa-thermometer-half',
    'camera': 'fa-camera',
    'hub': 'fa-network-wired',
    'wifi': 'fa-wifi',
    'tv': 'fa-tv',
    'mobile': 'fa-mobile',
    'phone': 'fa-mobile',
    'pc': 'fa-desktop',
    'computer': 'fa-desktop',
    'lock': 'fa-lock',
    'default': 'fa-microchip',
}


@register.filter(name='get_icon')
def get_icon(value):
    """Return a FontAwesome class based on the category/device type string.

    Matches keywords inside the provided value (case-insensitive).
    """
    if not value:
        return ICON_MAP['default']
    s = str(value).lower()
    for key, cls in ICON_MAP.items():
        if key == 'default':
            continue
        if key in s:
            return cls
    return ICON_MAP['default']
