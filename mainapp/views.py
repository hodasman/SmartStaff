from django.views.generic import TemplateView


class MainPageView(TemplateView):
    template_name = "mainapp/index.html"


class DevicesListView(TemplateView):
    template_name = "mainapp/devices_list.html"


class DevicesDetailView(TemplateView):
    template_name = "mainapp/device_details.html"


class ArticlesListView(TemplateView):
    template_name = "mainapp/articles.html"
