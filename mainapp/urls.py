from django.urls import path

from mainapp import views
from mainapp.apps import MainappConfig

app_name = MainappConfig.name

urlpatterns = [
    path("", views.MainPageView.as_view()),
    path("devices/", views.DevicesListView.as_view()),
    path(
        "devices/<int:pk>",
        views.DevicesDetailView.as_view(),
        name="news_detail",
    ),
    path("articles/", views.ArticlesListView.as_view()),
    path("articles/<int:pk>", views.ArticlesDetailView.as_view()),
    path("scenarios/", views.ScenariosListView.as_view()),
]
