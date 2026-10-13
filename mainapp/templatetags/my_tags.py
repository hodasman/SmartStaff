import re
from urllib.parse import urlsplit

import bleach
from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from mainapp import models as mainapp_models

register = template.Library()

ARTICLE_IMAGE_TOKEN = re.compile(r"\[\[article-image:(\d+)\]\]")
LOCAL_MEDIA_URL = re.compile(
    r"""(?P<prefix>\bsrc\s*=\s*["'])https?://(?:0\.0\.0\.0|127\.0\.0\.1|localhost)"""
    r"""(?::\d+)?(?P<path>/media/[^"']*)(?P<quote>["'])""",
    re.IGNORECASE,
)
ARTICLE_ALLOWED_TAGS = {
    "a",
    "blockquote",
    "br",
    "caption",
    "code",
    "dd",
    "del",
    "div",
    "dl",
    "dt",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "iframe",
    "i",
    "img",
    "li",
    "ol",
    "p",
    "pre",
    "s",
    "span",
    "strong",
    "sub",
    "sup",
    "table",
    "tbody",
    "td",
    "tfoot",
    "th",
    "thead",
    "tr",
    "u",
    "ul",
}
ARTICLE_ALLOWED_ATTRIBUTES = {
    "a": {"href", "title"},
    "iframe": {"allowfullscreen", "frameborder", "height", "src", "width"},
    "img": {"alt", "height", "src", "width"},
    "table": {"align", "border", "cellpadding", "cellspacing"},
}
ARTICLE_EMBED_HOSTS = {"www.youtube.com", "www.youtube-nocookie.com"}


@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """
    Return encoded URL parameters that are the same as the current
    request's parameters, only with the specified GET parameters added or changed.

    It also removes any empty parameters to keep things neat,
    so you can remove a parm by setting it to ``""``.

    For example, if you're on the page ``/things/?with_frosting=true&page=5``,
    then

    <a href="/things/?{% param_replace page=3 %}">Page 3</a>

    would expand to

    <a href="/things/?with_frosting=true&page=3">Page 3</a>

    Based on
    https://stackoverflow.com/questions/22734695/next-and-before-links-for-a-django-paginated-query/22735278#22735278
    """
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()

@register.simple_tag()
def get_article():
    return mainapp_models.Article.objects.all().order_by('created_at')


@register.filter
def render_article_text(text, article):
    """Sanitize article markup and render tokens for uploaded article images."""
    text = str(text or "")
    image_ids = {int(match.group(1)) for match in ARTICLE_IMAGE_TOKEN.finditer(text)}
    images = {
        image.pk: image
        for image in article.images.filter(pk__in=image_ids)
    }
    parts = []
    position = 0
    for match in ARTICLE_IMAGE_TOKEN.finditer(text):
        parts.append(_sanitize_article_html(text[position:match.start()]))
        image = images.get(int(match.group(1)))
        if image is None:
            parts.append(_sanitize_article_html(match.group(0)))
        else:
            parts.append(
                format_html(
                    '<img src="{}" alt="{}" class="img-fluid article-inline-image" '
                    'style="max-height:600px;width:auto;max-width:100%;object-fit:contain;">',
                    image.image.url,
                    image.alt or "",
                )
            )
        position = match.end()
    parts.append(_sanitize_article_html(text[position:]))
    return mark_safe("".join(parts))


def _sanitize_article_html(text):
    text = LOCAL_MEDIA_URL.sub(
        lambda match: f"{match.group('prefix')}{match.group('path')}{match.group('quote')}",
        text,
    )
    sanitized = bleach.clean(
        text,
        tags=ARTICLE_ALLOWED_TAGS,
        attributes=_is_allowed_article_attribute,
        protocols={"http", "https", "mailto"},
        strip=True,
        strip_comments=True,
    )
    return mark_safe(sanitized.replace("\n", "<br>\n"))


def _is_allowed_article_attribute(tag, name, value):
    if name not in ARTICLE_ALLOWED_ATTRIBUTES.get(tag, set()):
        return False
    if tag == "iframe" and name == "src":
        parsed_url = urlsplit(value)
        return (
            parsed_url.scheme == "https"
            and parsed_url.hostname in ARTICLE_EMBED_HOSTS
            and parsed_url.path.startswith("/embed/")
        )
    return True