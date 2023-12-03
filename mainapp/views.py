from django.views.generic import DetailView, ListView, TemplateView

from mainapp import models as mainapp_models


class MainPageView(TemplateView):
    template_name = "mainapp/index.html"


class DevicesListView(ListView):
    model = mainapp_models.Devices


class DevicesDetailView(DetailView):
    model = mainapp_models.Devices


class ArticlesListView(TemplateView):
    template_name = "mainapp/articles.html"


class ArticlesDetailView(TemplateView):
    template_name = "mainapp/article_details.html"


class ScenariosListView(TemplateView):
    template_name = "mainapp/scenarios.html"
