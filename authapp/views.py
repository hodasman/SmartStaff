from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import UserPassesTestMixin
# from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.utils.safestring import mark_safe
from django.views import View
from django.views.generic import CreateView, TemplateView, UpdateView

from authapp import forms
from authapp.tasks import activate_email_task


class CustomLoginView(LoginView):
    def form_valid(self, form):
        ret = super().form_valid(form)
        message = f"Паспяхова!<br>Вітаю вас, {self.request.user.username}!"
        messages.add_message(self.request, messages.INFO, mark_safe(message))
        return ret

    def form_invalid(self, form):
        for _unused, msg in form.error_messages.items():
            messages.add_message(
                self.request,
                messages.WARNING,
                mark_safe(f"Что-то пошло не так:<br>{msg}"),
            )
        return self.render_to_response(self.get_context_data(form=form))


class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.add_message(self.request, messages.INFO, "Да сустрэчы!")
        return super().dispatch(request, *args, **kwargs)


class RegisterView(SuccessMessageMixin, CreateView):
    model = get_user_model()
    form_class = forms.CreateUserForm
    success_message = "Мае віншаванні! Цяпер у Вас есць свой асабісты кабінет у Смарт-хаце!"
    # template_name = "authapp/signup.html"

    def get_success_url(self):
        return reverse_lazy("authapp:signup_done")

    def form_valid(self, form):
        user: User = form.save()
        user.is_active = False
        user.save()
        activate_email_task(user)
        return HttpResponseRedirect(self.get_success_url())


class RegisterDoneView(TemplateView):  
    template_name = "authapp/signup_done.html"
    extra_context = {"title": "Регистрация завершена, активируйте учётную запись."}


class RegisterConfirmView(View): 
    def get(self, request, uidb64, token):  
        User = get_user_model() 
        try:  
            uid = urlsafe_base64_decode(uidb64)  
            user = User.objects.get(pk=uid)  
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):  
            user = None  
        if user is not None and default_token_generator.check_token(user, token):  
            user.is_active = True  
            user.save()  
            login(request, user)  
            return render(  
                request,  
                "authapp/signup_confirmed.html",  
                {"title": "Учётная запись активирована."},  
            )  
        else:  
            return render(  
                request,  
                "authapp/signup_not_confirmed.html",  
                {"title": "Ошибка активации учётной записи."},  
            )


class ProfileEditView(UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = get_user_model()
    form_class = forms.UserChangeForm
    success_message = "Вашыя даныя паспяхова зменены!"

    def test_func(self):
        return True if self.request.user.pk == self.kwargs.get("pk") else False

    def get_success_url(self):
        return reverse_lazy("authapp:profile_edit", args=[self.request.user.pk])
