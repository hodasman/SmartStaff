import logging

from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordResetConfirmView,
                                       PasswordResetView)
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import CreateView, UpdateView

from authapp import forms
from authapp.forms import CustomPasswordResetForm, CustomSetPasswordForm
from authapp.tasks import activate_email_task

logger = logging.getLogger(__name__)


class CustomLoginView(LoginView):
    def form_valid(self, form):
        ret = super().form_valid(form)
        message = _("Login success!<br>Hi, {username}!")
        # format_html экранирует аргументы, оставляя HTML только в самом шаблоне
        final_message = format_html(message, username=self.request.user.username)
        messages.add_message(self.request, messages.INFO, final_message)
        return ret

    def form_invalid(self, form):
        for _unused, msg in form.error_messages.items():
            messages.add_message(
                self.request,
                messages.WARNING,
                format_html(_("Something goes wrong:<br>{msg}"), msg=msg),
            )
        return self.render_to_response(self.get_context_data(form=form))


class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.add_message(self.request, messages.INFO, _("See you later!"))
        return super().dispatch(request, *args, **kwargs)


class RegisterView(SuccessMessageMixin, CreateView):
    model = get_user_model()
    form_class = forms.CreateUserForm

    def get_success_url(self):
        return reverse_lazy("authapp:login")

    def form_valid(self, form):
        self.object = form.save()
        # Письмо шлётся синхронно: если SMTP/API недоступен, нельзя падать 500-й —
        # аккаунт уже создан. Логируем и сообщаем пользователю.
        try:
            activate_email_task(request=self.request, user=self.object)
        except Exception:
            logger.exception(
                "Activation email sending failed for user %s", self.object.email
            )
            message = _(
                "Your account has been created, but the activation email could "
                "not be sent. Please contact the site administrator."
            )
            messages.add_message(self.request, messages.WARNING, message)
        else:
            message = _("A link to activate your account has been sent to your email.")
            messages.add_message(self.request, messages.INFO, message)
        return HttpResponseRedirect(self.get_success_url())


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
            message = _('Congratulations! You now have your own personal account in Smart House!')
            messages.add_message(self.request, messages.SUCCESS, message)
            return redirect('mainapp:personal_page', username=user.username)
        else:  
            message = _('Account activation error! Make sure you used the correct link from the email you were sent!')
            messages.add_message(self.request, messages.WARNING, message)
            return redirect('authapp:login')


class ProfileEditView(UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = get_user_model()
    form_class = forms.UserChangeForm
    success_message = _("Your data has been successfully changed!")

    def test_func(self):
        return True if self.request.user.pk == self.kwargs.get("pk") else False

    def get_success_url(self):
        return reverse_lazy("authapp:profile_edit", args=[self.request.user.pk])


class CustomPasswordResetView(PasswordResetView):  
    template_name = 'registration/password_reset.html'  
    email_template_name = 'registration/password_reset_email.html'  
    form_class = CustomPasswordResetForm  
    success_url = reverse_lazy('authapp:password_reset_done')  


class CustomUserPasswordResetConfirmView(PasswordResetConfirmView):  
    template_name = 'registration/password_reset_confirm.html'  
    success_url = reverse_lazy('authapp:password_reset_complete')  
    form_class = CustomSetPasswordForm