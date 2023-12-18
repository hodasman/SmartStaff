from django.views.generic import DetailView, ListView, TemplateView

from mainapp import models as mainapp_models


class MainPageView(TemplateView):
    template_name = "mainapp/index.html"


class DevicesListView(ListView):
    model = mainapp_models.Devices

    def get_context_data(self, **kwargs):
        context = super(DevicesListView, self).get_context_data(**kwargs)
        context["qty"] = len(mainapp_models.Devices.objects.all())  # Количество устройств
        return context


class DevicesCategory(ListView):
    model = mainapp_models.Devices
    template_name = "mainapp/devices_list.html"

    def get_queryset(self):
        """cat__slug – это способ обращения к слагу таблицы DeviceCategory через объект category модели Devices
        функция выдает объект QuerySet с выборкой по категории"""
        return mainapp_models.Devices.objects.filter(category__slug=self.kwargs["cat_slug"], deleted=False)


class DevicesDetailView(DetailView):
    model = mainapp_models.Devices

    def get_context_data(self, **kwargs):
        context = super(DevicesDetailView, self).get_context_data(**kwargs)
        context["qty"] = len(mainapp_models.Devices.objects.all())  # Количество устройств
        return context


class ArticlesListView(TemplateView):
    template_name = "mainapp/articles.html"


class ArticlesDetailView(TemplateView):
    template_name = "mainapp/article_details.html"


class ScenariosListView(TemplateView):
    template_name = "mainapp/scenarios.html"
