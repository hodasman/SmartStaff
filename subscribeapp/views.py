import logging

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
        try:
            # Письмо-подтверждение подписчику. Подписка сохраняется
            # даже если отправка не удалась (например, SMTP не настроен)
            send_subscribe_confirm_email(form.instance.email)
        except Exception:
            logger.exception("Не удалось отправить письмо о подписке на %s", form.instance.email)
        return ret
    

class SubscribeViewRight(SubscribeView):
    '''Вьюха для подписки в правом блоке в блоге'''
    form_class = SubscribeFormRight