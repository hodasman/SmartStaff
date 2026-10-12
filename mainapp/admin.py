import json

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404, HttpResponseNotAllowed, JsonResponse
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from authapp import models as authapp_models
from mainapp import models as mainapp_models

MAX_ARTICLE_IMAGE_SIZE = 10 * 1024 * 1024


def validate_article_image_size(image):
    if image and image.size > MAX_ARTICLE_IMAGE_SIZE:
        raise ValidationError(
            _("Image file size must not exceed 10 MiB."),
            code="article_image_too_large",
        )


class ArticleAdminForm(forms.ModelForm):
    class Meta:
        model = mainapp_models.Article
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        upload_url = ""
        if self.instance.pk:
            upload_url = reverse(
                "admin:mainapp_article_upload_image",
                args=(self.instance.pk,),
            )
        self.fields["text"].widget.attrs["data-image-upload-url"] = upload_url


class ArticleImageAdminForm(forms.ModelForm):
    class Meta:
        model = mainapp_models.ArticleImage
        fields = "__all__"

    def clean_image(self):
        image = self.cleaned_data.get("image")
        validate_article_image_size(image)
        return image


class ScenarioImageInline(admin.TabularInline):
    model = mainapp_models.ScenarioImage
    extra = 1
    readonly_fields = ("created_at", "preview")
    fields = ("image", "preview", "alt", "is_main", "order")

    def preview(self, obj):
        if not obj or not obj.image:
            return ""
        try:
            url = obj.image.url
        except Exception:
            return ""
        return format_html('<img src="{}" style="max-height:100px;"/>', url)

    preview.short_description = "Preview"


class RequiredDeviceInline(admin.TabularInline):
    model = mainapp_models.RequiredDevice
    extra = 1
    fields = ("device", "quantity", "note")


class ScenarioVariantInline(admin.TabularInline):
    model = mainapp_models.ScenarioVariant
    extra = 1
    readonly_fields = ("created_at",)
    fields = ("platform", "title", "description", "created_at")


@admin.register(mainapp_models.ScenarioVariant)
class ScenarioVariantAdmin(admin.ModelAdmin):
    list_display = ("id", "scenario", "platform")
    inlines = [RequiredDeviceInline]
    list_per_page = 20


@admin.register(mainapp_models.Scenario)
class ScenariosAdmin(admin.ModelAdmin):
    list_per_page = 10
    filter_horizontal = ("device_types",)
    inlines = [ScenarioImageInline, ScenarioVariantInline]

class DeviceImageInline(admin.TabularInline):
    model = mainapp_models.DeviceImage
    extra = 1
    readonly_fields = ("created_at",)
    fields = ("image", "alt", "is_main", "order")


class ArticleImageInline(admin.TabularInline):
    model = mainapp_models.ArticleImage
    form = ArticleImageAdminForm
    extra = 1
    readonly_fields = ("created_at",)
    fields = ("image", "alt", "is_main", "order")


class PurchaseLinkInline(admin.TabularInline):
    model = mainapp_models.PurchaseLink
    extra = 1
    fields = ("marketplace", "url", "affiliate")


class DeviceAdminForm(forms.ModelForm):
    """Форма устройства: тип (device_type) должен относиться к выбранной категории."""

    class Meta:
        model = mainapp_models.Device
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Карта "id категории -> [id типов]" для JS-цепочки select'ов в админке
        mapping = {}
        for t in mainapp_models.DeviceType.objects.only("id", "category_id"):
            mapping.setdefault(str(t.category_id), []).append(str(t.pk))
        # В админке FK-виджет обёрнут в RelatedFieldWidgetWrapper (иконка "+"),
        # который не пробрасывает свои attrs во внутренний select — вешаем на внутренний
        widget = self.fields["device_type"].widget
        if isinstance(widget, RelatedFieldWidgetWrapper):
            widget = widget.widget
        widget.attrs["data-category-map"] = json.dumps(mapping)

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        device_type = cleaned_data.get("device_type")
        if category and device_type and device_type.category_id != category.pk:
            self.add_error(
                "device_type",
                ValidationError(
                    "Тип «%(type)s» относится к категории «%(type_category)s». "
                    "Выберите тип из категории «%(category)s» или измените категорию.",
                    code="device_type_category_mismatch",
                    params={
                        "type": device_type,
                        "type_category": device_type.category,
                        "category": category,
                    },
                ),
            )
        return cleaned_data


@admin.register(mainapp_models.Device)
class DevicesAdmin(admin.ModelAdmin):
    form = DeviceAdminForm
    list_display = ["id", "title", "slug", "is_legacy", "deleted"]
    list_per_page = 10
    ordering = ["title"]
    search_fields = ("title", "model_name")
    list_filter = ("is_legacy", "deleted")
    list_editable = ("is_legacy", "deleted")
    filter_horizontal = ("protocols",)
    inlines = [DeviceImageInline, PurchaseLinkInline]

    class Media:
        js = ("js/category_type_chaining.js",)

@admin.register(mainapp_models.Article)
class ArticlesAdmin(admin.ModelAdmin):
    form = ArticleAdminForm
    list_per_page = 20
    list_display = ("id", "title", "slug", "category", "author", "created_at", "deleted")
    list_filter = ("category", "author", "deleted", "created_at")
    search_fields = ("title", "preambule", "text")
    raw_id_fields = ("author",)
    inlines = [ArticleImageInline]
    ordering = ("-created_at",)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<path:object_id>/upload-image/",
                self.admin_site.admin_view(self.upload_image),
                name="mainapp_article_upload_image",
            ),
        ]
        return custom_urls + urls

    def upload_image(self, request, object_id):
        if request.method != "POST":
            return HttpResponseNotAllowed(["POST"])

        article = self.get_object(request, object_id)
        if article is None:
            raise Http404
        if not self.has_change_permission(request, article):
            raise PermissionDenied

        try:
            image = forms.ImageField().clean(request.FILES.get("image"))
            validate_article_image_size(image)
            alt = forms.CharField(max_length=255, required=False).clean(
                request.POST.get("alt", "")
            )
        except ValidationError as error:
            return JsonResponse({"error": error.messages[0]}, status=400)

        article_image = mainapp_models.ArticleImage.objects.create(
            article=article,
            image=image,
            alt=alt,
        )
        return JsonResponse(
            {
                "id": article_image.pk,
                "alt": article_image.alt or "",
                "url": article_image.image.url,
            }
        )

    class Media:
        js = ("js/article_image_upload_v3.js",)


@admin.register(mainapp_models.Platform)
class PlatformsAdmin(admin.ModelAdmin):
    list_per_page = 10

@admin.register(mainapp_models.Idea)
class PlatformsAdmin(admin.ModelAdmin):
    list_per_page = 10

@admin.register(authapp_models.User)
class UserAdmin(admin.ModelAdmin):
    list_per_page = 10

@admin.register(mainapp_models.ArticleCategory)
class ArticleCategoryAdmin(admin.ModelAdmin):
    list_per_page = 10

@admin.register(mainapp_models.DeviceCategory)
class DeviceCategory(admin.ModelAdmin):
    list_per_page = 10

@admin.register(mainapp_models.DeviceType)
class DeviceType(admin.ModelAdmin):
    list_per_page = 10


@admin.register(mainapp_models.Protocol)
class ProtocolAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "slug")
    list_per_page = 20

@admin.register(mainapp_models.RatingStar)
class RatingStar(admin.ModelAdmin):
    list_per_page = 10

@admin.register(mainapp_models.ArticleComment)
class ArticleComment(admin.ModelAdmin):
    list_per_page = 10

@admin.register(mainapp_models.ScenarioComment)
class ScenarioComment(admin.ModelAdmin):
    list_per_page = 10

@admin.register(mainapp_models.Feedback)
class Feedback(admin.ModelAdmin):
    list_per_page = 10
    list_display = ('email', 'ip_address', 'user', 'name')
    list_display_links = ('email', 'ip_address')