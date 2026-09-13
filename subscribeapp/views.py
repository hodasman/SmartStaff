import logging
import threading

from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView

from .forms import SubscribeForm, SubscribeFormRight
from .models import Subscribers
from .services import send_subscribe_confirm_email

logger = logging.getLogger(__name__)


class SubscribeView(CreateView):
    model = Subscribers
    form_class = SubscribeForm
    success_url = reverse_lazy("mainapp:main_page")

    def form_valid(self, form):
        ret = super().form_valid(form)
        message = _("You have subscribed to the newsletter!")
        messages.add_message(self.request, messages.INFO, mark_safe(message))
        # Письмо-подтверждение отправляем в фоновом потоке: недоступный или
        # медленный SMTP не должен задерживать ответ пользователю
        threading.Thread(
            target=send_subscribe_confirm_email,
            args=(form.instance.email,),
            daemon=True,
        ).start()
        return ret
    

class SubscribeViewRight(SubscribeView):
    '''Вьюха для подписки в правом блоке в блоге'''
    form_class = SubscribeFormRight