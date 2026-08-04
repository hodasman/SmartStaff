from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey


class MenuItem(MPTTModel):
    name = models.CharField(max_length=100, unique=True)
    url = models.CharField(_("link"), max_length=255)
    cat_slug = models.CharField(
        _("category slug "),
        max_length=255,
        null=True,
        blank=True,
    )
    position = models.PositiveIntegerField(_("Position"), default=1)
    parent = TreeForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")

    class MPTTMeta:
        order_insertion_by = ["position"]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Menu item")
        verbose_name_plural = _("Menu items")
