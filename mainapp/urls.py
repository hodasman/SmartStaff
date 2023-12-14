from django.urls import path

from mainapp import views
from mainapp.apps import MainappConfig

app_name = MainappConfig.name

urlpatterns = [
    path("", views.MainPageView.as_view(), name="main_page"),
    path("devices/", views.DevicesListView.as_view(), name="devices-list"),
    path(
        "devices/<slug:slug>",
        views.DevicesDetailView.as_view(),
        name="devices_detail",
    ),
    path("devices/category/<slug:cat_slug>/", views.DevicesCategory.as_view(), name="devices_category"),
    path("articles/", views.ArticlesListView.as_view(), name="articles"),
    path("articles/<int:pk>", views.ArticlesDetailView.as_view(), name="article_detail"),
    path("scenarios/", views.ScenariosListView.as_view(), name="scenarios"),
]
