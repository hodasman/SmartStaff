import django_filters
from django.utils.translation import gettext_lazy as _

from mainapp.models import Device


class DevicesFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(label=_('Search by name'), field_name='title', lookup_expr='contains')
    def __init__(self, *args, **kwargs):
        super(DevicesFilter, self).__init__(*args, **kwargs)

    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('created_at', _('By date')),
            ('title', _('By name')),
        ),

        label = _('Sorting')
    )
    o.descending_fmt = _("%s (back)")
    
    class Meta:
        model = Device
        fields = {
            'category',
            'ecosystem',
        }
        