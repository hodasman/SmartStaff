from django.views.generic import TemplateView


class MainPageView(TemplateView):
    template_name = "mainapp/index.html"


class DevicesListView(TemplateView):
    template_name = "mainapp/devices_list.html"
