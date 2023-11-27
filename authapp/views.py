from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.utils.safestring import mark_safe


class CustomLoginView(LoginView):
    def form_valid(self, form):
        ret = super().form_valid(form)
        message = f"Успешный вход!<br>Привет, {self.request.user.username}"
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
        messages.add_message(self.request, messages.INFO, "Увидимся!")
        return super().dispatch(request, *args, **kwargs)
