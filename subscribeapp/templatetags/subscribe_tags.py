from django import template

from subscribeapp.forms import SubscribeForm, SubscribeFormRight

register=template.Library()

@register.inclusion_tag("subscribe/tags/form.html")
def subscribe_form():
    return {"subscribe_form": SubscribeForm()}

@register.inclusion_tag("subscribe/tags/form_right.html")
def subscribe_form_2():
    return {"subscribe_form_2": SubscribeFormRight()}