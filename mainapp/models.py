from autoslug import AutoSlugField
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Count, Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager


def device_foto_path(instance, filename):
    # file will be uploaded to
    #   MEDIA_ROOT / devices_foto / <model> / <filename>
    return "devices_foto/{0}/{1}".format(instance.model, filename)


def article_img_path(instance, filename):
    # file will be uploaded to
    #   MEDIA_ROOT / articles_img / <slug> / <filename>
    return "articles_img/{0}/{1}".format(instance.slug, filename)

def scenarios_img_path(instance, filename):
    # file will be uploaded to
    #   MEDIA_ROOT / scenarios_img / <slug> / <filename>
    return "scenarios_img/{0}/{1}".format(instance.slug, filename)


class Platform(models.Model):
    title = models.CharField(max_length=256, verbose_name=_("Name"), db_index=True)
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Platform")
        verbose_name_plural = _("Platforms")
        ordering = ["title"]

    def __str__(self) -> str:
        return f"{self.title}"
    
    def qty_scenarios_in_platform(self):
        '''Возвращает количество сценариев по платформе'''
        # count ScenarioVariant entries linked to this platform
        from .models import ScenarioVariant
        qty = ScenarioVariant.objects.filter(platform__id=self.id).count()
        return qty


class Idea(models.Model):
    title = models.CharField(max_length=256, verbose_name=_("Name"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Idea")
        verbose_name_plural = _("Ideas")
        ordering = ["title"]

    def __str__(self) -> str:
        return f"{self.title}"


class ArticleCategory(models.Model):
    title = models.CharField(max_length=256, verbose_name=_("Name"))
    slug = AutoSlugField(populate_from="title", unique=True, db_index=True)
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Article category")
        verbose_name_plural = _("Article categories")
        ordering = ["title"]

    def __str__(self) -> str:
        return f"{self.title}"
    
    def qty_articles_in_category(self):
        qty = Article.objects.filter(category__slug=self.slug).count()
        return qty


class DeviceCategory(models.Model):
    title = models.CharField(max_length=256, verbose_name=_("Name"))
    slug = AutoSlugField(populate_from="title")
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Device category")
        verbose_name_plural = _("Device categories")
        ordering = ["title"]

    def __str__(self) -> str:
        return f"{self.title}"


class DeviceType(models.Model):
    category = models.ForeignKey(
        DeviceCategory,
        on_delete=models.CASCADE,
        related_name="device_types",
        verbose_name=_("Category"),
    )
    title = models.CharField(
        max_length=256,
        verbose_name=_("Name"),
    )
    slug = AutoSlugField(populate_from="title")
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Description"),
    )

    class Meta:
        verbose_name = _("Device type")
        verbose_name_plural = _("Device types")
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


class ObjectManager(models.Manager):
    use_for_related_fields = True
 
    def search(self, query=None):
        qs = self.get_queryset()
        if query:
            or_lookup = (Q(title__icontains=query) | Q(text__icontains=query))
            qs = qs.filter(or_lookup)
 
        return qs


# Custom queryset + manager for Article to support soft-delete semantics
class ArticleQuerySet(models.QuerySet):
    def active(self):
        # guard: only filter if model has `deleted` field
        if any(f.name == 'deleted' for f in self.model._meta.get_fields()):
            return self.filter(deleted=False)
        return self

    def with_deleted(self):
        return self.all()

    def search(self, query=None):
        qs = self
        if query:
            or_lookup = (Q(title__icontains=query) | Q(text__icontains=query))
            qs = qs.filter(or_lookup)
        return qs


class ArticleManager(models.Manager):
    def get_queryset(self):
        qs = ArticleQuerySet(self.model, using=self._db)
        if any(f.name == 'deleted' for f in self.model._meta.get_fields()):
            return qs.filter(deleted=False)
        return qs

    def with_deleted(self):
        return ArticleQuerySet(self.model, using=self._db)

    def search(self, query=None):
        return self.get_queryset().search(query)


class Article(models.Model):
    objects = ArticleManager()
    title = models.CharField(max_length=256, verbose_name=_("Name"))
    category = models.ForeignKey(
        ArticleCategory, verbose_name=_("Category"), on_delete=models.CASCADE, related_name="articles"
    )
    slug = AutoSlugField(populate_from="title", verbose_name="URL", unique=True)
    preambule = models.TextField(verbose_name=_("Brief description"), blank=True)
    text = models.TextField(verbose_name=_("Text"), blank=True)
    main_img = models.ImageField(verbose_name=_("Main picture"), blank=True, null=True, upload_to=article_img_path)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Author"), blank=True, null=True)
    tags = TaggableManager()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created", editable=False, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Edited", editable=False)
    deleted = models.BooleanField(default=False, db_index=True)

    def __str__(self) -> str:
        return f"{self.pk} {self.title}"

    def delete(self, *args):
        self.deleted = True
        self.save()

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
        ordering = ["title"]
    
    def get_absolute_url(self):
        return f'/mainapp/articles/{self.slug}'
    
    def get_all_comments(self):
        '''Возвращает QuerySet объектов комментариев для данной статьи'''
        comments = ArticleComment.objects.filter(article_id = self.id)
        return comments


class ArticleImage(models.Model):
    article = models.ForeignKey(
        'mainapp.Article',
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Article'),
    )
    image = models.ImageField(verbose_name=_('Image'), upload_to=article_img_path)
    alt = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Alt text'))
    is_main = models.BooleanField(default=False, verbose_name=_('Main image'))
    order = models.PositiveSmallIntegerField(default=0, verbose_name=_('Order'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    class Meta:
        verbose_name = _('Article image')
        verbose_name_plural = _('Article images')
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.article.title} — image #{self.id}"


class Device(models.Model):
    category = models.ForeignKey(
        DeviceCategory,
        verbose_name=_("Category"),
        on_delete=models.CASCADE,
        related_name="devices"
    )
    device_type = models.ForeignKey(
        DeviceType,
        on_delete=models.PROTECT,
        related_name="devices",
        verbose_name=_("Device type"),
    )
    title = models.CharField(max_length=256, verbose_name=_("Title"))
    slug = AutoSlugField(populate_from="title", verbose_name=_("URL"))
    description = models.TextField(verbose_name=_("Description"), blank=True)
    icon = models.ImageField(verbose_name=_("Device icon"), blank=True, null=True, upload_to=device_foto_path)
    model_name = models.CharField(max_length=256, verbose_name=_("Device model"))
    size = models.CharField(max_length=256, verbose_name=_("Dimensions"))
    power = models.CharField(max_length=256, verbose_name=_("Power supply"))
    protocols = models.ManyToManyField('Protocol', verbose_name=_("Supported protocols"), blank=True)
    temperature = models.CharField(max_length=256, verbose_name=_("Operating temperature"))
    ecosystem = models.ManyToManyField(Platform, verbose_name=_("Ecosystem"), blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Author"),
        blank=True,
        null=True
    )
    package_contents = models.TextField(verbose_name=_("Package contents"))
    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(verbose_name=_("Created"), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_("Updated"), auto_now=True)

    class Meta:
        verbose_name = _("Device")
        verbose_name_plural = _("Devices")
        ordering = ["title"]

    def __str__(self):
        return self.title


def device_image_path(instance, filename):
    # сохраняем в MEDIA_ROOT / devices_foto / <device-slug> / <filename>
    slug = getattr(instance.device, 'slug', instance.device.id)
    return f"devices_foto/{slug}/{filename}"


class DeviceImage(models.Model):
    device = models.ForeignKey(
        "mainapp.Device",
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Device"),
    )
    image = models.ImageField(upload_to=device_image_path, verbose_name=_("Image"))
    alt = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Alt text"))
    is_main = models.BooleanField(default=False, verbose_name=_("Main image"))
    order = models.PositiveSmallIntegerField(default=0, verbose_name=_("Order"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))

    class Meta:
        verbose_name = _("Device image")
        verbose_name_plural = _("Device images")
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.device.title} — image #{self.id}"


class Protocol(models.Model):
    title = models.CharField(max_length=64, verbose_name=_("Name"))
    slug = models.SlugField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = _("Protocol")
        verbose_name_plural = _("Protocols")
        ordering = ["title"]

    def __str__(self):
        return self.title


class PurchaseLink(models.Model):
    MARKETPLACE_OZON = 'ozon'
    MARKETPLACE_WB = 'wb'
    MARKETPLACE_ALI = 'aliexpress'
    MARKETPLACE_OTHER = 'other'

    MARKETPLACE_CHOICES = [
        (MARKETPLACE_OZON, 'Ozon'),
        (MARKETPLACE_WB, 'Wildberries'),
        (MARKETPLACE_ALI, 'AliExpress'),
        (MARKETPLACE_OTHER, 'Other'),
    ]

    device = models.ForeignKey(
        "mainapp.Device",
        on_delete=models.CASCADE,
        related_name="purchase_links",
        verbose_name=_("Device"),
    )
    marketplace = models.CharField(max_length=32, choices=MARKETPLACE_CHOICES, verbose_name=_("Marketplace"))
    url = models.URLField(verbose_name=_("URL"))
    # price and currency removed because marketplace prices are dynamic
    affiliate = models.BooleanField(default=False, verbose_name=_("Affiliate"))
    note = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Note"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))

    class Meta:
        verbose_name = _("Purchase link")
        verbose_name_plural = _("Purchase links")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.get_marketplace_display()} — {self.device.title}"


# Custom queryset + manager for Scenario to support soft-delete semantics
class ScenarioQuerySet(models.QuerySet):
    def active(self):
        if any(f.name == 'deleted' for f in self.model._meta.get_fields()):
            return self.filter(deleted=False)
        return self

    def with_deleted(self):
        return self.all()

    def search(self, query=None):
        qs = self
        if query:
            or_lookup = (Q(title__icontains=query) | Q(text__icontains=query))
            qs = qs.filter(or_lookup)
        return qs


class ScenarioManager(models.Manager):
    def get_queryset(self):
        qs = ScenarioQuerySet(self.model, using=self._db)
        if any(f.name == 'deleted' for f in self.model._meta.get_fields()):
            return qs.filter(deleted=False)
        return qs

    def with_deleted(self):
        return ScenarioQuerySet(self.model, using=self._db)

    def search(self, query=None):
        return self.get_queryset().search(query)


class Scenario(models.Model):
    objects = ScenarioManager()
    title = models.CharField(max_length=256, verbose_name=_("Title"))
    slug = AutoSlugField(populate_from="title", verbose_name=_("URL"))
    text = models.TextField(verbose_name=_("Text"), blank=True)
    description = models.TextField(verbose_name=_("Description"), blank=True)
    main_img = models.ImageField(verbose_name=_("Main image"), blank=True, null=True, upload_to=scenarios_img_path)
    devices = models.ManyToManyField(Device)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Author"), blank=True, null=True)
    # `platform` removed: scenario may have multiple variants per ecosystem
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, blank=True, null=True)
    tags = TaggableManager()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"), editable=False, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"), editable=False, db_index=True)
    deleted = models.BooleanField(default=False, db_index=True)

    def __str__(self) -> str:
        return f"{self.pk} {self.title}"

    def delete(self, *args):
        self.deleted = True
        self.save()

    class Meta:
        verbose_name = _("Scenario")
        verbose_name_plural = _("Scenarios")
        ordering = ["title"]
        # Составной индекс для часто используемых фильтров
        indexes = [
            models.Index(fields=['deleted', '-created_at']),
            models.Index(fields=['author', 'deleted']),
            models.Index(fields=['deleted', 'created_at']),
        ]

    def next(self):
        return self.get_next_by_created_at()

    def pre(self):
        return self.get_previous_by_created_at()
    
    def get_absolute_url(self):
        return reverse('mainapp:scenario-detail', kwargs={'slug': self.slug})
    
    def get_rating(self) -> int:
        query = Rating.objects.filter(scenario=self.id)
        sum = 0
        for item in query:
            sum += item.star.value
        return sum//len(query)
    
    def get_quantity_devices(self,):
        qty = len(self.devices.all())
        if qty in [11, 12, 13, 14]:
            return 'Устройств'
        if qty % 10 == 1:
            return 'Устройство'
        if qty % 10 in [2, 3, 4]:
            return 'Устройства'
        else:
            return 'Устройств'
        
    def get_all_comments(self):
        '''Возвращает QuerySet объектов комментариев для данного сценария'''
        comments = ScenarioComment.objects.filter(scenario_id = self.id)
        return comments
    
    def get_similar_scenarios(self, limit=5):
        '''
        Функция ищет похожие сценарии устройства которых такие же как и заданного сценария.
        Возвращает список сценариев которые можно реализовать из этих же устройств или 
        сценариев где нужно докупить несколько устройств
        '''
        
        # Получить ID устройств текущего сценария
        device_ids = self.devices.values_list('id', flat=True)
        
        if not device_ids:
            return Scenario.objects.none()
        
        # Найти сценарии с общими устройствами, отсортировав по количеству общих
        return (
            Scenario.objects
            .exclude(id=self.id)
            .filter(devices__in=device_ids)
            .annotate(common_count=Count('devices', filter=Q(devices__in=device_ids)))
            .order_by('-common_count')
            .distinct()[:limit]
        )


class ScenarioImage(models.Model):
    scenario = models.ForeignKey(
        'mainapp.Scenario',
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Scenario'),
    )
    image = models.ImageField(verbose_name=_('Image'), upload_to=scenarios_img_path)
    alt = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Alt text'))
    is_main = models.BooleanField(default=False, verbose_name=_('Main image'))
    order = models.PositiveSmallIntegerField(default=0, verbose_name=_('Order'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    class Meta:
        verbose_name = _('Scenario image')
        verbose_name_plural = _('Scenario images')
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.scenario.title} — image #{self.id}"



class ScenarioVariant(models.Model):
    """Вариант реализации сценария для конкретной экосистемы (platform).
    Содержит связь на конкретные устройства или типы устройств через RequiredDevice.
    """
    scenario = models.ForeignKey(
        'mainapp.Scenario', on_delete=models.CASCADE, related_name='variants', verbose_name=_('Scenario')
    )
    platform = models.ForeignKey(
        Platform, on_delete=models.CASCADE, related_name='scenario_variants', verbose_name=_('Platform')
    )
    title = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Title'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    class Meta:
        verbose_name = _('Scenario variant')
        verbose_name_plural = _('Scenario variants')
        unique_together = (('scenario', 'platform'),)

    def __str__(self) -> str:
        return f"{self.scenario.title} — {self.platform.title}"


class RequiredDevice(models.Model):
    """Требуемое устройство (конкретное или по типу) для варианта сценария.
    Указывайте либо `device`, либо `device_type`, но не оба одновременно.
    """
    variant = models.ForeignKey(
        ScenarioVariant, on_delete=models.CASCADE, related_name='required_devices', verbose_name=_('Variant')
    )
    device = models.ForeignKey(
        Device, on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Device')
    )
    device_type = models.ForeignKey(
        DeviceType, on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Device type')
    )
    quantity = models.PositiveSmallIntegerField(default=1, verbose_name=_('Quantity'))
    note = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Note'))

    class Meta:
        verbose_name = _('Required device')
        verbose_name_plural = _('Required devices')

    def clean(self):
        # ensure at least one of device or device_type is set
        if not self.device and not self.device_type:
            raise ValidationError(_('Either device or device_type must be set.'))
        if self.device and self.device_type:
            raise ValidationError(_('Specify only one of device or device_type, not both.'))

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)
    

class RatingStar(models.Model):
    '''Звезда рейтинга(1-5)'''
    value  = models.SmallIntegerField("Значение", default=0)

    def __str__(self) -> str:
        return f'{self.value}'

    class Meta:
        verbose_name = _("Rating star")
        verbose_name_plural = _("Rating stars")
        ordering = ["-value"]


class Rating(models.Model):
    '''Рейтинг'''
    ip = models.CharField('IP Адрес', max_length=15)
    star = models.ForeignKey(RatingStar, on_delete=models.CASCADE, verbose_name=_("Star"))
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, verbose_name=_("Scenario"))

    def __str__(self) -> str:
        return f'{self.scenario} - {self.star}'
    
    class Meta:
        verbose_name = "Рейтинг"
        verbose_name_plural = "Рейтинги"
        

class ArticleComment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name=_("Article"))
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Comment author"))
    content = models.TextField(verbose_name=_("Text"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Comment date"))

    class Meta:
        db_table = "article_comments"
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")



class ScenarioComment(models.Model):
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, verbose_name=_("Scenario"))
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Comment author"))
    content = models.TextField(verbose_name=_("Text"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Comment date"))

    class Meta:
        db_table = "scenario_comments"
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")


class Feedback(models.Model):
    """
    Модель обратной связи
    """
    subject = models.CharField(max_length=255, verbose_name=_("Subject"))
    email = models.EmailField(max_length=255, verbose_name=_("Email"))
    content = models.TextField(verbose_name=_("Message"))
    time_create = models.DateTimeField(auto_now_add=True, verbose_name=_("Sent at"))
    ip_address = models.GenericIPAddressField(verbose_name=_("Sender IP"), blank=True, null=True)
    name = models.CharField(verbose_name=_("Sender name"), max_length=20, blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _("Feedback")
        verbose_name_plural = _("Feedback")
        ordering = ['-time_create']

    def __str__(self):
        return f'Вам письмо от {self.email}'