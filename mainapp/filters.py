import django_filters
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from mainapp.models import Device


class DevicesFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(label=_('Search by name'), field_name='title', lookup_expr='contains')

    def __init__(self, *args, **kwargs):
        super(DevicesFilter, self).__init__(*args, **kwargs)
        # create OrderingFilter at runtime so labels are translated for the
        # active locale (gettext evaluates the current language)
        self.filters['o'] = django_filters.OrderingFilter(
            # tuple-mapping retains order
            fields=(
                ('created_at', gettext('By date')),
                ('title', gettext('By name')),
            ),
            label=gettext('Sorting')
        )
        self.filters['o'].descending_fmt = gettext("%s (back)")

    class Meta:
        model = Device
        fields = {
            'category',
            'ecosystem',
        }
        