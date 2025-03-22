from django.contrib import admin

from .models import Subscribers


@admin.register(Subscribers)
class SubscribersAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ("email", "date")
