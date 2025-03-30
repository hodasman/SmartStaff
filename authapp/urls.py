from django.urls import path

from authapp import views
from authapp.apps import AuthappConfig

app_name = AuthappConfig.name

urlpatterns = [
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path(  
        "signup_done/", views.RegisterDoneView.as_view(), name="signup_done"  
    ),  
    path(  
        "signup_confirm/<uidb64>/<token>/",  
        views.RegisterConfirmView.as_view(),  
        name="signup_confirm",  
    ),
    path(
        "profile_edit/<int:pk>/",
        views.ProfileEditView.as_view(),
        name="profile_edit",
    ),
]
