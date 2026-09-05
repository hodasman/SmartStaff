import json

import django_filters
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from mainapp.models import Device, DeviceType, Platform, Protocol


class DevicesFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(label=_('Search by name'), field_name='title', lookup_expr='contains')

    # Одиночный select вместо <select multiple>: у multiple нет пустого варианта,
    # а nice-select на фронте превращает его в обычный список, из которого
    # после выбора уже не «снять» фильтр. С "---------" фильтр можно очистить.
    ecosystem = django_filters.ModelChoiceFilter(
        label=_('Ecosystem'),
        field_name='ecosystem',
        queryset=Platform.objects.all(),
    )
    protocols = django_filters.ModelChoiceFilter(
        label=_('Supported protocols'),
        field_name='protocols',
        queryset=Protocol.objects.all(),
    )

    def __init__(self, *args, **kwargs):
        super(DevicesFilter, self).__init__(*args, **kwargs)

        # --- Тип устройства: согласован с категорией ----------------------
        # 1) Серверно: если выбрана категория, список типов ограничен ею
        category_id = None
        if self.data:
            try:
                category_id = int(self.data.get('category') or 0) or None
            except (TypeError, ValueError):
                category_id = None
        type_qs = DeviceType.objects.select_related('category')
        if category_id:
            type_qs = type_qs.filter(category__pk=category_id)

        # 2) Клиентски: карта "id категории -> [id типов]" для JS-цепочки
        #    select'ов (скрипт category_type_chaining.js)
        mapping = {}
        for t in DeviceType.objects.only('id', 'category_id'):
            mapping.setdefault(str(t.category_id), []).append(str(t.pk))

        device_type_filter = self.filters['device_type']
        device_type_filter.field.queryset = type_qs
        device_type_filter.field.widget.attrs['data-category-map'] = json.dumps(mapping)
        # -------------------------------------------------------------------

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
        # список (не set) — сохраняет порядок полей в форме фильтра
        fields = [
            'category',
            'device_type',
            'ecosystem',
            'protocols',
        ]