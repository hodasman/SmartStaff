from django.urls import path

from subscribeapp.apps import SubscribeappConfig

from .views import SubscribeView

app_name = SubscribeappConfig.name

urlpatterns = [
    path("", SubscribeView.as_view(), name="subscribe")
]