from django import template

from subscribeapp.forms import SubscribeForm

register=template.Library()


@register.inclusion_tag("subscribe/tags/form.html")
def subscribe_form():
    return {"subscribe_form": SubscribeForm()}