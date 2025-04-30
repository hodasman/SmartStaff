from django.urls import path

from mainapp import views
from mainapp.apps import MainappConfig

app_name = MainappConfig.name

urlpatterns = [
    path("", views.MainPageView.as_view(), name="main_page"),
    path("personal-page/<str:username>", views.view_personal_page, name="personal_page"),
    path("devices/", views.filtered_devices, name="devices-list"),
    path(
        "devices/<slug:slug>",
        views.DevicesDetailView.as_view(),
        name="devices_detail",
    ),
    path("devices/category/<slug:cat_slug>/", views.DevicesCategory.as_view(), name="devices_category"),
    path("articles/", views.ArticlesListView.as_view(), name="articles"),
    path("articles/<slug:slug>", views.ArticlesDetailView.as_view(), name="article_detail"),
    path("articles/category/<slug:cat_slug>/", views.ArticlesCategory.as_view(), name="articles_category"),
    path("scenarios/", views.ScenariosListView.as_view(), name="scenarios"),
    path("scenarios/<slug:slug>", views.ScenariosDetailView.as_view(), name="scenario_detail"),
    path("scenarios/category/<int:platform_id>/", views.ScenariosCategory.as_view(), name="scenarios_category"),
    path("search/", views.ESearchView.as_view(), name="search"),
    path("add-rating/", views.AddStarRating.as_view(), name='add_rating'),
    path("articles/<int:article_id>/comment/", views.add_comment_article, name="comment_article"),
    path("scenarios/<int:scenario_id>/comment/", views.add_comment_scenario, name="comment_scenario"),
    path('add-device/<str:slug>/', views.add_device_to_user, name='add_device'),
    path('delete-device/<str:slug>/', views.delete_device_user, name='delete_device'),
    path('tag/<str:tag_slug>/', views.tag_list, name='list_by_tag'),
    path('contact/', views.FeedbackCreateView.as_view(), name='contact'),
]
