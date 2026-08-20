from django.contrib import admin
from django.utils.html import format_html

from authapp import models as authapp_models
from mainapp import models as mainapp_models


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
    inlines = [ScenarioImageInline, ScenarioVariantInline]

class DeviceImageInline(admin.TabularInline):
    model = mainapp_models.DeviceImage
    extra = 1
    readonly_fields = ("created_at",)
    fields = ("image", "alt", "is_main", "order")


class ArticleImageInline(admin.TabularInline):
    model = mainapp_models.ArticleImage
    extra = 1
    readonly_fields = ("created_at",)
    fields = ("image", "alt", "is_main", "order")


class PurchaseLinkInline(admin.TabularInline):
    model = mainapp_models.PurchaseLink
    extra = 1
    fields = ("marketplace", "url", "affiliate")


@admin.register(mainapp_models.Device)
class DevicesAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "slug", "deleted"]
    list_per_page = 10
    ordering = ["title"]
    search_fields = ("title", "model_name")
    filter_horizontal = ("protocols",)
    inlines = [DeviceImageInline, PurchaseLinkInline]

@admin.register(mainapp_models.Article)
class ArticlesAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ("id", "title", "slug", "category", "author", "created_at", "deleted")
    list_filter = ("category", "author", "deleted", "created_at")
    search_fields = ("title", "preambule", "text")
    raw_id_fields = ("author",)
    inlines = [ArticleImageInline]
    ordering = ("-created_at",)

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