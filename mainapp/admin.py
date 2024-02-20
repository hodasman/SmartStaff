from django.contrib import admin

from authapp import models as authapp_models
from mainapp import models as mainapp_models


@admin.register(mainapp_models.Scenarios)
class ScenariosAdmin(admin.ModelAdmin):
    list_per_page = 10

@admin.register(mainapp_models.Devices)
class DevicesAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "slug", "deleted"]
    list_per_page = 10
    ordering = ["title"]

@admin.register(mainapp_models.Articles)
class ArticlesAdmin(admin.ModelAdmin):
    list_per_page = 10

@admin.register(mainapp_models.Platforms)
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

@admin.register(mainapp_models.RatingStar)
class RatingStar(admin.ModelAdmin):
    list_per_page = 10