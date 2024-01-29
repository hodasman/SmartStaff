import django_filters
from django.utils.translation import gettext_lazy as _

from mainapp.models import Devices


class DevicesFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(label='Поиск по названию', field_name='title', lookup_expr='contains')
    def __init__(self, *args, **kwargs):
        super(DevicesFilter, self).__init__(*args, **kwargs)

    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('created_at', 'По дате'),
            ('title', 'По названию'),
        ),

        label = 'Сортировка'
    )
    o.descending_fmt = _("%s (обратный)")
    
    class Meta:
        model = Devices
        fields = {
            
            'category',
            'platforms',
            'author',
        }
        