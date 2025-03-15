from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic import CreateView

from .forms import SubscribeForm
from .models import Subscribers


class SubscribeView(CreateView):
    model = Subscribers
    form_class = SubscribeForm
    success_url = reverse_lazy("mainapp:main_page")

    def form_valid(self, form):
        ret = super().form_valid(form)
        message = "Вы падпісаліся на рассылку навін!"
        messages.add_message(self.request, messages.INFO, mark_safe(message))
        return ret
