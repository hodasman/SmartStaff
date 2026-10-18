from itertools import chain

from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import transaction
from django.db.models import Prefetch, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DetailView, ListView, TemplateView
from taggit.models import Tag

from mainapp import models as mainapp_models
from mainapp.filters import DevicesFilter
from mainapp.forms import (
    CommentForm,
    FeedbackCreateForm,
    OnboardingAnswerForm,
    OnboardingDeviceSelectionForm,
    OnboardingEcosystemSelectionForm,
    RaitingForm,
)
from mainapp.services.email import send_contact_email_message
from mainapp.services.utils import get_client_ip


class MainPageView(TemplateView):
    template_name = "mainapp/index.html"

    def get_context_data(self, **kwargs):
        context = super(MainPageView, self).get_context_data(**kwargs)
        context["devices"] = (
            mainapp_models.Device.objects.select_related("category").all()[:4]
        )
        context["scenarios"] = mainapp_models.Scenario.objects.prefetch_related(
            Prefetch(
                "images",
                queryset=mainapp_models.ScenarioImage.objects.order_by(
                    "-is_main", "order", "id"
                ),
            )
        )[:4]
        context["articles"] = mainapp_models.Article.objects.prefetch_related(
            Prefetch(
                "images",
                queryset=mainapp_models.ArticleImage.objects.order_by(
                    "-is_main", "order", "id"
                ),
            )
        )[:4]
        return context


@login_required
def onboarding_start(request):
    form = OnboardingAnswerForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        request.session.pop("onboarding_device_ids", None)
        has_devices = form.cleaned_data["has_devices"]
        request.session["onboarding_has_devices"] = has_devices
        if has_devices == "yes":
            return redirect("mainapp:onboarding_devices")
        return redirect("mainapp:onboarding_ecosystems")

    return render(
        request,
        "mainapp/onboarding_start.html",
        {"form": form},
    )


@login_required
def onboarding_devices(request):
    if request.session.get("onboarding_has_devices") != "yes":
        return redirect("mainapp:onboarding_start")

    search_query = request.GET.get("q", "").strip()
    devices = (
        mainapp_models.Device.objects.filter(deleted=False)
        .select_related("category", "device_type")
        .order_by("title")
    )
    if search_query:
        devices = devices.filter(
            Q(title__icontains=search_query)
            | Q(model_name__icontains=search_query)
            | Q(description__icontains=search_query)
        )
    devices_page = Paginator(devices, 30).get_page(request.GET.get("page"))

    if request.method == "POST":
        form = OnboardingDeviceSelectionForm(request.POST)
        if form.is_valid():
            selected_device_ids = list(
                form.cleaned_data["devices"].values_list("pk", flat=True)
            )
            request.session["onboarding_device_ids"] = selected_device_ids
            search_query = request.POST.get("q", "").strip()
            if request.POST.get("action") == "search":
                search_url = reverse("mainapp:onboarding_devices")
                if search_query:
                    search_url = f"{search_url}?{urlencode({'q': search_query})}"
                return redirect(search_url)
            if request.POST.get("action") == "page":
                page_url = reverse("mainapp:onboarding_devices")
                page_params = {"page": request.POST.get("page", "1")}
                if search_query:
                    page_params["q"] = search_query
                return redirect(f"{page_url}?{urlencode(page_params)}")
            if not selected_device_ids:
                form.add_error("devices", _("Select at least one device."))
            else:
                return redirect("mainapp:onboarding_ecosystems")

        selected_device_ids = set(request.POST.getlist("devices"))
        search_query = request.POST.get("q", "").strip()
        if search_query:
            devices = devices.filter(
                Q(title__icontains=search_query)
                | Q(model_name__icontains=search_query)
                | Q(description__icontains=search_query)
            )
    else:
        form = OnboardingDeviceSelectionForm()
        if "onboarding_device_ids" in request.session:
            selected_device_ids = {
                str(device_id)
                for device_id in request.session["onboarding_device_ids"]
            }
        else:
            selected_device_ids = {
                str(device_id)
                for device_id in request.user.devices.filter(
                    deleted=False
                ).values_list("pk", flat=True)
            }

    visible_device_ids = {str(device.pk) for device in devices_page}
    hidden_selected_device_ids = selected_device_ids - visible_device_ids

    return render(
        request,
        "mainapp/onboarding_devices.html",
        {
            "form": form,
            "devices": devices_page,
            "devices_page": devices_page,
            "search_query": search_query,
            "selected_device_ids": selected_device_ids,
            "hidden_selected_device_ids": hidden_selected_device_ids,
        },
    )


_ONBOARDING_HUB_ECOSYSTEM_ALIASES = {
    "Apple Home (with Hub)": "Apple Home (HomeKit)",
    "Yandex Alice (with Hub)": "Yandex Alice",
}


def _onboarding_ecosystems():
    return mainapp_models.Platform.objects.exclude(
        title__icontains="(with hub)"
    )


def _compatible_onboarding_ecosystems(device_ids):
    selected_devices = list(
        mainapp_models.Device.objects.filter(
            pk__in=device_ids,
            deleted=False,
        ).prefetch_related("ecosystem")
    )
    if len(selected_devices) != len(set(device_ids)):
        return None

    platform_ids_by_title = dict(
        mainapp_models.Platform.objects.values_list("title", "pk")
    )
    compatible_ids = None
    for device in selected_devices:
        device_ecosystem_ids = set()
        for ecosystem in device.ecosystem.all():
            base_title = _ONBOARDING_HUB_ECOSYSTEM_ALIASES.get(
                ecosystem.title
            )
            if base_title is None:
                device_ecosystem_ids.add(ecosystem.pk)
            elif base_title in platform_ids_by_title:
                device_ecosystem_ids.add(
                    platform_ids_by_title[base_title]
                )
        compatible_ids = (
            device_ecosystem_ids
            if compatible_ids is None
            else compatible_ids & device_ecosystem_ids
        )

    if not compatible_ids:
        return mainapp_models.Platform.objects.none()
    return _onboarding_ecosystems().filter(pk__in=compatible_ids).order_by(
        "title"
    )


@login_required
def onboarding_ecosystems(request):
    has_devices = request.session.get("onboarding_has_devices")
    if has_devices is None:
        has_devices = "no"
        request.session["onboarding_has_devices"] = has_devices
    elif has_devices not in {"yes", "no"}:
        return redirect("mainapp:onboarding_start")

    device_ids = request.session.get("onboarding_device_ids", [])
    if has_devices == "yes" and not device_ids:
        return redirect("mainapp:onboarding_devices")
    if device_ids:
        ecosystems = _compatible_onboarding_ecosystems(device_ids)
        if ecosystems is None:
            request.session.pop("onboarding_device_ids", None)
            request.session.pop("onboarding_has_devices", None)
            messages.error(
                request,
                _("The selected device list is no longer available. Please select your devices again."),
            )
            return redirect("mainapp:onboarding_devices")
    else:
        ecosystems = _onboarding_ecosystems()

    form = OnboardingEcosystemSelectionForm(
        request.POST or None,
        ecosystems=ecosystems,
    )
    if request.method == "POST" and form.is_valid():
        ecosystem = form.cleaned_data["ecosystem"]
        selected_devices = mainapp_models.Device.objects.filter(
            pk__in=device_ids,
            deleted=False,
        )
        with transaction.atomic():
            request.user.devices.add(*selected_devices)
            request.user.ecosystem = ecosystem
            request.user.onboarding_completed = True
            request.user.save(
                update_fields=[
                    "ecosystem",
                    "onboarding_completed",
                ]
            )
        request.session.pop("onboarding_device_ids", None)
        request.session.pop("onboarding_has_devices", None)
        return redirect(
            "mainapp:personal_page",
            username=request.user.username,
        )

    return render(
        request,
        "mainapp/onboarding_ecosystems.html",
        {
            "form": form,
            "ecosystems": ecosystems,
            "has_selected_devices": bool(device_ids),
        },
    )


class DevicesListView(ListView):
    model = mainapp_models.Device
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["qty"] = mainapp_models.Device.objects.filter(
            deleted=False
        ).count()

        return context


class DevicesCategory(ListView):
    model = mainapp_models.Device
    template_name = "mainapp/devices_list.html"
    paginate_by = 5

    def get_queryset(self):
        return mainapp_models.Device.objects.filter(
            device_type__category__slug=self.kwargs["cat_slug"],
            deleted=False,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        category = mainapp_models.DeviceCategory.objects.get(
            slug=self.kwargs["cat_slug"]
        )

        context["cat_name"] = category.title

        context["qty"] = mainapp_models.Device.objects.filter(
            device_type__category=category,
            deleted=False,
        ).count()

        return context


class DevicesDetailView(DetailView):
    model = mainapp_models.Device

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["qty"] = mainapp_models.Device.objects.filter(
            deleted=False
        ).count()

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
        context['comments'] = mainapp_models.ArticleComment.objects.filter(article_id = context["object"].id)
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
        return mainapp_models.Article.objects.filter(category__slug=self.kwargs["cat_slug"])

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
        context['similar_scenarios'] = context["object"].get_similar_scenarios() # сценарии с этими же типами устройств
        return context
    

class ScenariosCategory(ListView):
    model = mainapp_models.Scenario
    template_name = "mainapp/scenario_list.html"
    paginate_by = 5

    def get_queryset(self):
        """Получаем объект QuerySet выборку сценариев по категории (платформе)"""
        return mainapp_models.Scenario.objects.filter(platform__id=self.kwargs["platform_id"])

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

        # --- Подбор сценариев под устройства пользователя -----------------
        # Сценарий можно реализовать, если у пользователя есть устройства
        # нужных типов (либо не хватает 1-2 типов, которые можно докупить).
        # Совместимость по протоколам проверяется для устройств, участвующих
        # в конкретном сценарии: они должны уметь общаться по одному общему
        # протоколу (пересечение протоколов непустое). Устройства пользователя
        # вне сценария не мешают его реализации.
        user_devices = list(
            current_user.devices.select_related('device_type').prefetch_related('protocols')
        )
        user_device_types = {d.device_type_id for d in user_devices}

        scenarios_for_user = []  # сценарии, для которых хватает устройств или не хватает 1-2 типов
        if user_device_types:
            for scenario in mainapp_models.Scenario.objects.all():
                scenario_types = set(scenario.device_types.values_list('id', flat=True))
                if not scenario_types:
                    continue

                # типы, которых нет у пользователя (нужно докупить устройства этих типов)
                missing_types = scenario_types - user_device_types
                if len(missing_types) > 2:
                    continue

                # Пересечение протоколов устройств, участвующих в сценарии.
                # Устройства без указанных протоколов в проверке не участвуют.
                # common_protocols = None — проверить совместимость нельзя.
                common_protocols = None
                for device in user_devices:
                    if device.device_type_id not in scenario_types or not device.protocols.exists():
                        continue
                    device_protocols = set(device.protocols.values_list('id', flat=True))
                    common_protocols = device_protocols if common_protocols is None else common_protocols & device_protocols

                if common_protocols is not None and not common_protocols:
                    # участвующие устройства не умеют общаться друг с другом
                    continue

                # Для недостающих типов проверяем, что в каталоге есть устройство
                # этого типа с совместимым протоколом — иначе сценарий не
                # реализовать даже после покупки
                if missing_types and common_protocols:
                    compatible_types = set(
                        mainapp_models.Device.objects.filter(
                            device_type_id__in=missing_types,
                            protocols__in=common_protocols,
                            deleted=False,
                        ).values_list('device_type_id', flat=True)
                    )
                    if not missing_types.issubset(compatible_types):
                        continue

                # missing_count используется в get_missing_types_display
                scenario.missing_count = len(missing_types)
                scenarios_for_user.append(scenario)

            scenarios_for_user.sort(key=lambda scenario: scenario.missing_count)

        context['scenarios_for_user'] = scenarios_for_user
        # -------------------------------------------------------------------

        #Пагинация
        paginator = Paginator(current_user.devices.all(), 4)  # Показывать по 4 устройств на странице
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return render(request, 'mainapp/personal_page.html', context)
    else:
        messages.error(request, _('To enter your personal account, you need to log in'))
        return redirect('mainapp:main_page')
    

def add_device_to_user(request, slug):
    current_user = request.user
    device = get_object_or_404(mainapp_models.Device, slug=slug)
    if current_user.is_authenticated:
        if current_user not in device.user_set.all():
            # В таблице authapp_usr_devices необходимо сделать соответствующую запись
            current_user.devices.add(device)
            current_user.save()
            messages.info(request, _('Device %(device_title)s added to your list') % {'device_title': device.title})
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            messages.info(request, _('The device is already on your list.!'))
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, _('To add a device to the list, you need to log in'))
        return redirect('authapp:login')
    

def delete_device_user(request, slug):
    current_user = request.user
    device = get_object_or_404(mainapp_models.Device, slug=slug)
    if device in current_user.devices.all():
        current_user.devices.remove(device)
        current_user.save()
        messages.info(request, _('Device %(device_title)s removed from your list') % {'device_title': device.title})
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        messages.info(request, _('Device %(device_title)s not on your list') % {'device_title': device.title})
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
    success_message = _('Your request has been successfully sent!')
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