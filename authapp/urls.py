from django.contrib.auth import views as auth_views
from django.urls import path

from authapp import views
from authapp.apps import AuthappConfig

app_name = AuthappConfig.name

urlpatterns = [
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
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
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password-reset'),  
    path('password_reset_confirm/<uidb64>/<token>/',  
        views.CustomUserPasswordResetConfirmView.as_view(),  
        name='password_reset_confirm'),  
    path('password_reset_complete/',  
        auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),  
        name='password_reset_complete'),  
    path('password-reset/done/',  
        auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),  
        name='password_reset_done'),
]
