from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import render
from django.views.generic import DetailView, ListView, TemplateView

from mainapp import models as mainapp_models
from mainapp.filters import DevicesFilter


class MainPageView(TemplateView):
    template_name = "mainapp/index.html"


class DevicesListView(ListView):
    model = mainapp_models.Devices
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(DevicesListView, self).get_context_data(**kwargs)
        context["qty"] = len(mainapp_models.Devices.objects.all())  # Количество устройств
        return context


class DevicesCategory(ListView):
    model = mainapp_models.Devices
    template_name = "mainapp/devices_list.html"
    paginate_by = 5

    def get_queryset(self):
        """cat__slug – это способ обращения к слагу таблицы DeviceCategory через объект category модели Devices
        функция выдает объект QuerySet с выборкой по категории"""
        return mainapp_models.Devices.objects.filter(category__slug=self.kwargs["cat_slug"], deleted=False)

    def get_context_data(self, **kwargs):
        context = super(DevicesCategory, self).get_context_data(**kwargs)
        context["cat_name"] = mainapp_models.DeviceCategory.objects.get(
            slug=self.kwargs["cat_slug"]
        ).title  # Получение названия категории
        context["qty"] = len(mainapp_models.Devices.objects.filter(category__slug=self.kwargs["cat_slug"], deleted=False)) # Количество устройств в категории
        return context


class DevicesDetailView(DetailView):
    model = mainapp_models.Devices

    def get_context_data(self, **kwargs):
        context = super(DevicesDetailView, self).get_context_data(**kwargs)
        context["qty"] = len(mainapp_models.Devices.objects.all())  # Количество устройств
        return context


class ArticlesListView(ListView):
    model = mainapp_models.Articles
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(ArticlesListView, self).get_context_data(**kwargs)
        context["all_categories"] = mainapp_models.ArticleCategory.objects.all()
        return context


class ArticlesDetailView(DetailView):
    model = mainapp_models.Articles

    def get_context_data(self, **kwargs):
        context = super(ArticlesDetailView, self).get_context_data(**kwargs)
        context["all_categories"] = mainapp_models.ArticleCategory.objects.all()
        return context


class ArticlesCategory(ListView):
    model = mainapp_models.Articles
    template_name = "mainapp/articles_list.html"
    paginate_by = 5

    def get_queryset(self):
        """cat__slug – это способ обращения к слагу таблицы ArticleCategory через объект category модели Articles
        функция выдает объект QuerySet с выборкой по категории"""
        return mainapp_models.Articles.objects.filter(category__slug=self.kwargs["cat_slug"], deleted=False)

    def get_context_data(self, **kwargs):
        context = super(ArticlesCategory, self).get_context_data(**kwargs)
        context["cat_name"] = mainapp_models.ArticleCategory.objects.get(
            slug=self.kwargs["cat_slug"]
        ).title  # Получение названия категории
        context["all_categories"] = mainapp_models.ArticleCategory.objects.all()
        return context


class ScenariosListView(ListView):
    model = mainapp_models.Scenarios
    paginate_by = 5


class ScenariosDetailView(DetailView):
    model = mainapp_models.Scenarios
    

    def get_context_data(self, **kwargs):
        context = super(ScenariosDetailView, self).get_context_data(**kwargs)
        try:
            context["next"] = self.get_object().next()
        except Exception:
            context["next"] = self.model.objects.first()
        try:
            context["prev"] = self.get_object().pre()
        except Exception:
            context["prev"] = self.model.objects.last()
        return context
    

def filtered_devices(request):
    '''
    Пагинация работает благодаря templatetags/my_tags.py. Так как этот плагин копирует гет параметры всех фильтров 
    и передает его в ссылки на кнопках пагинатора. В шаблоне - param_replace
    '''
    f = DevicesFilter(request.GET, queryset=mainapp_models.Devices.objects.all())
    paginator = Paginator(f.qs, 10)
    page = request.GET.get('page', 1)
    try:
        response = paginator.page(page)
    except PageNotAnInteger:
        response = paginator.page(1)
    except EmptyPage:
        response = paginator.page(paginator.num_pages)
    context = {'filter': response,'filter_form':f, 'qty': len(f.qs)}
    return render(request, 'mainapp/devices_filter.html', context)

# class DevicesFilteredViews(ListFilteredView):
#     filter_set = DevicesFilter
#     model = mainapp_models.Devices
#     template_name = "mainapp/devices_form.html"
#     paginate_by = 5

class SearchArticlesView(ListView):
    model = mainapp_models.Articles
    template_name = 'mainapp/search.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        object_list = mainapp_models.Articles.objects.filter(
            Q(title__icontains=query) | Q(text__icontains=query)
        )
        return object_list
    
    def get_context_data(self, **kwargs):
        context = super(SearchArticlesView, self).get_context_data(**kwargs)
        context["total_results"] = self.get_queryset().count()
        return context