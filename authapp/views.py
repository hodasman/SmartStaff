import logging

from urllib.parse import quote

from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordChangeView,
                                       PasswordResetConfirmView,
                                       PasswordResetView)
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.html import format_html
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import CreateView, FormView, UpdateView

from authapp import forms
from authapp.forms import CustomPasswordResetForm, CustomSetPasswordForm
from authapp.tasks import activate_email_task, email_change_task

logger = logging.getLogger(__name__)


class CustomLoginView(LoginView):
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # AuthenticationForm берёт label из capfirst(verbose_name), а
        # verbose_name у email не обёрнут в gettext — задаём сами.
        form.fields["username"].label = _("Email")
        form.fields["username"].widget.attrs["placeholder"] = _("Enter Email")
        form.fields["password"].widget.attrs["placeholder"] = _("Password")
        return form

    def form_valid(self, form):
        ret = super().form_valid(form)
        message = _("Login success!<br>Hi, {username}!")
        # format_html экранирует аргументы, оставляя HTML только в самом шаблоне
        final_message = format_html(message, username=self.request.user.username)
        messages.add_message(self.request, messages.INFO, final_message)
        return ret

    def form_invalid(self, form):
        # Неактивный аккаунт (письмо потеряно / ссылка истекла):
        # предлагаем выслать ссылку активации повторно.
        # Внимание: form.user_cache не подходит — ModelBackend возвращает
        # None для неактивного юзера, поэтому ищем в БД напрямую.
        user = None
        username = form.data.get("username", "")
        if username:
            User = get_user_model()
            user = User.objects.filter(
                **{f"{User.USERNAME_FIELD}__iexact": username}
            ).first()
        if user is not None and not user.is_active:
            resend_url = reverse("authapp:resend_activation") + "?email=" + quote(
                user.email or ""
            )
            link = format_html(
                '<a href="{}">{}</a>', resend_url, _("Resend activation email")
            )
            messages.add_message(
                self.request,
                messages.WARNING,
                format_html(_("Your account is not activated. {link}"), link=link),
            )
        else:
            # Показываем только реально возникшие ошибки формы,
            # а не весь словарь form.error_messages (старый баг)
            for errors in form.errors.values():
                for msg in errors:
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
            # Явный backend: с двумя бэкендами (axes + ModelBackend)
            # login() без backend-аргумента даёт ValueError/500
            login(
                request,
                user,
                backend="django.contrib.auth.backends.ModelBackend",
            )  
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

    def form_valid(self, form):
        # Смена email НЕ применяется сразу: новый адрес сохраняется в
        # new_email и подтверждается по ссылке из письма. До подтверждения
        # старый адрес остаётся рабочим (защита от опечатки и перехвата).
        # Внимание: к моменту form_valid is_valid() уже применил данные к
        # form.instance, поэтому текущий адрес берём из БД, а не из instance.
        old_email = self.get_object().email
        requested_email = form.cleaned_data.get("email")
        email_changed = (
            requested_email and requested_email.lower() != old_email.lower()
        )
        self.object = form.save(commit=False)
        if email_changed:
            self.object.email = old_email
            self.object.new_email = requested_email
        self.object.save()
        if email_changed:
            try:
                email_change_task(request=self.request, user=self.object)
            except Exception:
                logger.exception(
                    "Email change confirmation failed for user %s", old_email
                )
                messages.add_message(
                    self.request,
                    messages.WARNING,
                    _(
                        "Could not send the confirmation email. Please try "
                        "again later or contact the site administrator."
                    ),
                )
            else:
                messages.add_message(
                    self.request,
                    messages.INFO,
                    _("A confirmation link has been sent to %(new_email)s. "
                      "Your email will change after you confirm it.")
                    % {"new_email": requested_email},
                )
        return HttpResponseRedirect(self.get_success_url())


class CustomPasswordResetView(PasswordResetView):  
    template_name = 'registration/password_reset.html'  
    email_template_name = 'registration/password_reset_email.html'  
    form_class = CustomPasswordResetForm  
    success_url = reverse_lazy('authapp:password_reset_done')  


class CustomUserPasswordResetConfirmView(PasswordResetConfirmView):  
    template_name = 'registration/password_reset_confirm.html'  
    success_url = reverse_lazy('authapp:password_reset_complete')  
    form_class = CustomSetPasswordForm




class ResendActivationView(FormView):
    """Повторная отправка письма активации на указанный email.

    Защита от перебора email: ответ одинаков и для существующего
    неактивированного аккаунта, и для любого другого адреса.
    """
    template_name = "registration/resend_activation.html"
    form_class = forms.ResendActivationForm
    success_url = reverse_lazy("authapp:login")

    def form_valid(self, form):
        user = form.get_user()
        if user is not None:
            try:
                activate_email_task(request=self.request, user=user)
            except Exception:
                logger.exception(
                    "Activation re-sending failed for user %s", user.email
                )
                messages.add_message(
                    self.request,
                    messages.WARNING,
                    _(
                        "Could not send the email. Please try again later or "
                        "contact the site administrator."
                    ),
                )
                return HttpResponseRedirect(self.get_success_url())
        messages.add_message(
            self.request,
            messages.INFO,
            _(
                "If this email belongs to an unactivated account, a new "
                "activation link has been sent."
            ),
        )
        return HttpResponseRedirect(self.get_success_url())


class PasswordChangeCustomView(LoginRequiredMixin, SuccessMessageMixin,
                               PasswordChangeView):
    """Смена пароля залогиненным пользователем из личного кабинета."""
    template_name = "registration/password_change_form.html"
    success_message = _("Your password has been changed successfully!")

    def get_success_url(self):
        return reverse("authapp:password_change_done")

    def form_valid(self, form):
        ret = super().form_valid(form)
        messages.add_message(
            self.request,
            messages.INFO,
            _("If you use other devices, log in on them again."),
        )
        return ret


class PasswordChangeDoneCustomView(LoginRequiredMixin, View):
    """Редирект в личный кабинет после смены пароля."""

    def get(self, request, *args, **kwargs):
        return redirect(
            reverse(
                "mainapp:personal_page", kwargs={"username": request.user.username}
            )
        )


from authapp.tokens import email_change_token_generator  # noqa: E402


class EmailChangeConfirmView(View):
    """Подтверждение смены email по ссылке из письма."""

    def get(self, request, uidb64, token):
        User = get_user_model()
        try:
            uid = urlsafe_base64_decode(uidb64)
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if (
            user is not None
            and user.new_email
            and email_change_token_generator.check_token(user, token)
        ):
            # повторная проверка уникальности: пока юзер думал, адрес
            # мог занять другой аккаунт
            if User.objects.filter(email__iexact=user.new_email).exclude(
                pk=user.pk
            ).exists():
                messages.add_message(
                    self.request,
                    messages.WARNING,
                    _("This email address is already taken by another account."),
                )
            else:
                old_email = user.email
                user.email = user.new_email
                user.new_email = None
                user.save(update_fields=["email", "new_email"])
                logger.info(
                    "User %s changed email from %s to %s",
                    user.username, old_email, user.email,
                )
                messages.add_message(
                    self.request,
                    messages.SUCCESS,
                    _("Your email address has been changed. Use the new "
                      "address to log in."),
                )
            return redirect(
                reverse(
                    "mainapp:personal_page",
                    kwargs={"username": user.username},
                )
            )
        messages.add_message(
            self.request,
            messages.WARNING,
            _("Email change confirmation error! The link is invalid or "
              "already used."),
        )
        return redirect("authapp:login")


class ResendEmailChangeView(LoginRequiredMixin, View):
    """Повторная отправка письма с подтверждением смены email."""

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.new_email:
            try:
                email_change_task(request=request, user=user)
            except Exception:
                logger.exception(
                    "Email change re-sending failed for user %s", user.email
                )
                messages.add_message(
                    self.request,
                    messages.WARNING,
                    _("Could not send the email. Please try again later or "
                      "contact the site administrator."),
                )
            else:
                messages.add_message(
                    self.request,
                    messages.INFO,
                    _("A confirmation link has been sent to %(new_email)s.")
                    % {"new_email": user.new_email},
                )
        return redirect(
            reverse(
                "mainapp:personal_page",
                kwargs={"username": user.username},
            )
        )
