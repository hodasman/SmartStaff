from itertools import chain

from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DetailView, ListView, TemplateView
from taggit.models import Tag

from mainapp import models as mainapp_models
from mainapp.filters import DevicesFilter
from mainapp.forms import CommentForm, FeedbackCreateForm, RaitingForm
from mainapp.services.email import send_contact_email_message
from mainapp.services.utils import get_client_ip


class MainPageView(TemplateView):
    template_name = "mainapp/index.html"

    def get_context_data(self, **kwargs):
        context = super(MainPageView, self).get_context_data(**kwargs)
        context["devices"] = mainapp_models.Device.objects.all()[:4]  # Устройства 4 шт
        context["scenarios"] = mainapp_models.Scenario.objects.all()[:4]  # Сценарии 4 шт
        context["articles"] = mainapp_models.Article.objects.all()[:4]  # Статьи 4 шт
        return context


class DevicesListView(ListView):
    model = mainapp_models.Device
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(DevicesListView, self).get_context_data(**kwargs)
        context["qty"] = len(mainapp_models.Device.objects.all())  # Количество устройств
        return context


class DevicesCategory(ListView):
    model = mainapp_models.Device
    template_name = "mainapp/devices_list.html"
    paginate_by = 5

    def get_queryset(self):
        """cat__slug – это способ обращения к слагу таблицы DeviceCategory через объект category модели Devices
        функция выдает объект QuerySet с выборкой по категории"""
        return mainapp_models.Device.objects.filter(category__slug=self.kwargs["cat_slug"], deleted=False)

    def get_context_data(self, **kwargs):
        context = super(DevicesCategory, self).get_context_data(**kwargs)
        context["cat_name"] = mainapp_models.DeviceCategory.objects.get(
            slug=self.kwargs["cat_slug"]
        ).title  # Получение названия категории
        context["qty"] = len(mainapp_models.Device.objects.filter(category__slug=self.kwargs["cat_slug"], deleted=False)) # Количество устройств в категории
        return context


class DevicesDetailView(DetailView):
    model = mainapp_models.Device

    def get_context_data(self, **kwargs):
        context = super(DevicesDetailView, self).get_context_data(**kwargs)
        context["qty"] = len(mainapp_models.Device.objects.all())  # Количество устройств
        return context


class ArticlesListView(ListView):
    model = mainapp_models.Article
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(ArticlesListView, self).get_context_data(**kwargs)
        context["all_categories"] = mainapp_models.ArticleCategory.objects.all()
        return context


class ArticlesDetailView(DetailView):
    model = mainapp_models.Article
    comment_form = CommentForm

    def get_context_data(self, **kwargs):
        context = super(ArticlesDetailView, self).get_context_data(**kwargs)
        context["all_categories"] = mainapp_models.ArticleCategory.objects.all()
        # context['comments'] = mainapp_models.ArticleComment.objects.filter(article_id = context["object"].id)
        user = auth.get_user(self.request)
        if user.is_authenticated:
            context['form'] = self.comment_form # передаем форму комментария
        try:
            context["next"] = self.get_object().next() # находим следующий объект
        except Exception:
            context["next"] = self.model.objects.first() # если его нет берем первый
        try:
            context["prev"] = self.get_object().pre()
        except Exception:
            context["prev"] = self.model.objects.last()

        return context


class ArticlesCategory(ListView):
    model = mainapp_models.Article
    template_name = "mainapp/articles_list.html"
    paginate_by = 5

    def get_queryset(self):
        """cat__slug – это способ обращения к слагу таблицы ArticleCategory через объект category модели Articles
        функция выдает объект QuerySet с выборкой по категории"""
        return mainapp_models.Article.objects.filter(category__slug=self.kwargs["cat_slug"], deleted=False)

    def get_context_data(self, **kwargs):
        context = super(ArticlesCategory, self).get_context_data(**kwargs)
        context["cat_name"] = mainapp_models.ArticleCategory.objects.get(
            slug=self.kwargs["cat_slug"]
        ).title  # Получение названия категории
        context["all_categories"] = mainapp_models.ArticleCategory.objects.all()
        return context


@login_required
@require_http_methods(["POST"])
def add_comment_article(request, article_id):
    """Представление для добавления комментария к статье"""
    form = CommentForm(request.POST)
    article = get_object_or_404(mainapp_models.Article, id=article_id)

    if form.is_valid():
        comment = mainapp_models.ArticleComment()
        comment.article = article
        comment.author = auth.get_user(request)
        comment.content = form.cleaned_data['comment_area']
        comment.save()
    return redirect(article.get_absolute_url())

@login_required
@require_http_methods(["POST"])
def add_comment_scenario(request, scenario_id):
    """Представление для добавления комментария к сценарию"""
    form = CommentForm(request.POST)
    scenario = get_object_or_404(mainapp_models.Scenario, id=scenario_id)

    if form.is_valid():
        comment = mainapp_models.ScenarioComment()
        comment.scenario = scenario
        comment.author = auth.get_user(request)
        comment.content = form.cleaned_data['comment_area']
        comment.save()
    return redirect(scenario.get_absolute_url())


class ScenariosListView(ListView):
    model = mainapp_models.Scenario
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(ScenariosListView, self).get_context_data(**kwargs)
        context["all_categories"] = mainapp_models.Platform.objects.all()
        return context


class ScenariosDetailView(DetailView):
    model = mainapp_models.Scenario
    comment_form = CommentForm

    def get_context_data(self, **kwargs):
        context = super(ScenariosDetailView, self).get_context_data(**kwargs)
        context['comments'] = mainapp_models.ScenarioComment.objects.filter(scenario_id = context["object"].id)
        try:
            context["next"] = self.get_object().next() # находим следующий объект
        except Exception:
            context["next"] = self.model.objects.first() # если его нет берем первый
        try:
            context["prev"] = self.get_object().pre()
        except Exception:
            context["prev"] = self.model.objects.last()

        context['star_form'] = RaitingForm() #форма звездного рейтинга из forms.py
        user = auth.get_user(self.request)
        if user.is_authenticated:
            context['form'] = self.comment_form # передаем форму комментария
        context["all_categories"] = mainapp_models.Platform.objects.all()
        context['similar_scenarios'] = context["object"].get_similar_scenarios() # сценарии с этими же устройствами
        return context
    

class ScenariosCategory(ListView):
    model = mainapp_models.Scenario
    template_name = "mainapp/scenario_list.html"
    paginate_by = 5

    def get_queryset(self):
        """Получаем объект QuerySet выборку сценариев по категории (платформе)"""
        return mainapp_models.Scenario.objects.filter(platform__id=self.kwargs["platform_id"], deleted=False)

    def get_context_data(self, **kwargs):
        context = super(ScenariosCategory, self).get_context_data(**kwargs)
        context["platform"] = mainapp_models.Platform.objects.get(
            id=self.kwargs["platform_id"]
        ).title  # Получение названия категории(платформы)
        context["all_categories"] = mainapp_models.Platform.objects.all()
        return context


def filtered_devices(request):
    '''
    Пагинация работает благодаря templatetags/my_tags.py. Так как этот плагин копирует гет параметры всех фильтров 
    и передает его в ссылки на кнопках пагинатора. В шаблоне - param_replace
    '''
    f = DevicesFilter(request.GET, queryset=mainapp_models.Device.objects.all())
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
    

class ESearchView(View):
    template_name = 'mainapp/search.html'
 
    def get(self, request, *args, **kwargs):
        context = {}
 
        q = request.GET.get('q')
        if q:
            query_sets = []  # Total QuerySet
 
            # Searching for all models
            query_sets.append(mainapp_models.Article.objects.search(query=q))
            query_sets.append(mainapp_models.Scenario.objects.search(query=q))
 
            # and combine results
            final_set = list(chain(*query_sets))
            final_set.sort(key=lambda x: x.created_at, reverse=True)  # Sorting
 
            context['last_question'] = '?q=%s' % q
            context['total_results'] = len(final_set)
 
            current_page = Paginator(final_set, 10)
 
            page = request.GET.get('page')
            try:
                context['object_list'] = current_page.page(page)
            except PageNotAnInteger:
                context['object_list'] = current_page.page(1)
            except EmptyPage:
                context['object_list'] = current_page.page(current_page.num_pages)
 
        return render(request=request, template_name=self.template_name, context=context)
    

class AddStarRating(View):
    """Добавление рейтинга сценарию"""
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def post(self, request):
        '''Создает новый объект модели Rating'''
        form = RaitingForm(request.POST)
        if form.is_valid():
            mainapp_models.Rating.objects.update_or_create(
                ip=self.get_client_ip(request),
                scenario_id=int(request.POST.get("scenario")),
                defaults={'star_id': int(request.POST.get("star"))}
            )
            return HttpResponse(status=201)
        else:
            return HttpResponse(status=400)
        

def view_personal_page(request, username):
    current_user = request.user
    if current_user.is_authenticated:
        context = {'user': current_user,  }
        user_devices = set(current_user.devices.all()) # Устройства юзера
        all_scenarios = mainapp_models.Scenario.objects.all() # Все сценарии в базе
        right_scenarios = [] #Список сценариев которые доступны юзеру
        almost_all = [] #Список сценариев где не хватает одного устройста
        for scenario in all_scenarios: # Ищем совпадения устройств юзера с устройствами сценариев
            scenario_devices = set(scenario.devices.all())
            common = user_devices.intersection(scenario_devices) # пересечения двух множеств(общие элементы)
            
            if len(common) == len(scenario_devices):
                right_scenarios.append(scenario)
            elif len(scenario_devices) - len(common) == 1:
                almost_all.append(scenario)
        context['right_scenarios'] = right_scenarios
        context['almost_all'] = almost_all
        #Пагинация
        paginator = Paginator(current_user.devices.all(), 4)  # Показывать по 4 устройств на странице
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return render(request, 'mainapp/personal_page.html', context)
    else:
        messages.error(request, 'Для входа в личный кабинет Вам необходимо авторизоваться')
        return redirect('mainapp:main_page')
    

def add_device_to_user(request, slug):
    current_user = request.user
    device = get_object_or_404(mainapp_models.Device, slug=slug)
    if current_user.is_authenticated:
        if current_user not in device.user_set.all():
            # В таблице authapp_usr_devices необходимо сделать соответствующую запись
            current_user.devices.add(device)
            current_user.save()
            messages.info(request, f'Устройство {device.title} добавленно в ваш список')
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            messages.info(request, f'Устройство уже есть в вашем списке!')
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, 'Для того чтобы добавить устройство в список, Вам необходимо авторизоваться')
        return redirect('authapp:login')
    

def delete_device_user(request, slug):
    current_user = request.user
    device = get_object_or_404(mainapp_models.Device, slug=slug)
    if device in current_user.devices.all():
        current_user.devices.remove(device)
        current_user.save()
        messages.info(request, f'Устройство {device.title} удалено из списка')
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        messages.info(request, f'Устройства {device.title} нет в вашем списке!')
        return redirect(request.META.get('HTTP_REFERER'))
    

def tag_list(request, tag_slug=None):
    '''Вьюха для страницы тегов. Выводит на страницу и статьи и сценарии по тегу'''
    query_sets = []
    tag = get_object_or_404(Tag, slug=tag_slug)
    query_sets.append(mainapp_models.Article.objects.filter(tags__in=[tag]))
    query_sets.append(mainapp_models.Scenario.objects.filter(tags__in=[tag]))
    final_set = list(chain(*query_sets))

    paginator = Paginator(final_set, 3) # 3 posts in each page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request, 'mainapp/list_tag.html', {'page': page,
                                                   'page_obj': posts,
                                                   'tag': tag,})


class FeedbackCreateView(SuccessMessageMixin, CreateView):
    '''Для страницы облратной связи'''
    model = mainapp_models.Feedback
    form_class = FeedbackCreateForm
    success_message = 'Ваш зварот паспяхова адпраўлены!'
    template_name = 'mainapp/contact.html'
    extra_context = {'title': 'Кантактная форма'}
    success_url = reverse_lazy('mainapp:contact')

    def form_valid(self, form):
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.ip_address = get_client_ip(self.request)
            if self.request.user.is_authenticated:
                feedback.user = self.request.user
            send_contact_email_message(feedback.subject, feedback.email, feedback.content, feedback.ip_address, feedback.user_id, feedback.name)
        return super().form_valid(form)
    

class AboutPageView(TemplateView):
    template_name = "mainapp/about.html"