import django_filters

from mainapp.models import Devices


class DevicesFilter(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
        super(DevicesFilter, self).__init__(*args, **kwargs)
        # self.form.fields['email'].label = "New Email Label"
    class Meta:
        model = Devices
        fields = {'platforms','author'}