from autoslug import AutoSlugField
from django.conf import settings
from django.db import models
from django.db.models import Q
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
    title = models.CharField(max_length=256, verbose_name=_("Name"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Platform")
        verbose_name_plural = _("Platforms")
        ordering = ["title"]

    def __str__(self) -> str:
        return f"{self.title}"
    
    def qty_scenarios_in_platform(self):
        '''Возвращает количество сценариев по платформе'''
        qty = len(Scenario.objects.filter(platform__id=self.id, deleted=False))
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
    slug = AutoSlugField(populate_from="title")
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Article category")
        verbose_name_plural = _("Article categories")
        ordering = ["title"]

    def __str__(self) -> str:
        return f"{self.title}"
    
    def qty_articles_in_category(self):
        qty = len(Article.objects.filter(category__slug=self.slug, deleted=False))
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


class Article(models.Model):
    objects = ObjectManager()
    title = models.CharField(max_length=256, verbose_name=_("Name"))
    category = models.ForeignKey(
        ArticleCategory, verbose_name=_("Category"), on_delete=models.CASCADE, related_name="articles"
    )
    slug = AutoSlugField(populate_from="title", verbose_name="URL")
    preambule = models.TextField(verbose_name=_("Brief description"), blank=True)
    text = models.TextField(verbose_name=_("Text"), blank=True)
    main_img = models.ImageField(verbose_name=_("Main picture"), blank=True, null=True, upload_to=article_img_path)
    img_1 = models.ImageField(verbose_name=_("Picture 1"), blank=True, null=True, upload_to=article_img_path)
    img_2 = models.ImageField(verbose_name=_("Picture 2"), blank=True, null=True, upload_to=article_img_path)
    img_3 = models.ImageField(verbose_name=_("Picture 3"), blank=True, null=True, upload_to=article_img_path)
    img_4 = models.ImageField(verbose_name=_("Picture 4"), blank=True, null=True, upload_to=article_img_path)
    img_5 = models.ImageField(verbose_name=_("Picture 5"), blank=True, null=True, upload_to=article_img_path)
    img_6 = models.ImageField(verbose_name=_("Picture 6"), blank=True, null=True, upload_to=article_img_path)
    img_7 = models.ImageField(verbose_name=_("Picture 7"), blank=True, null=True, upload_to=article_img_path)
    img_8 = models.ImageField(verbose_name=_("Picture 8"), blank=True, null=True, upload_to=article_img_path)
    img_9 = models.ImageField(verbose_name=_("Picture 9"), blank=True, null=True, upload_to=article_img_path)
    img_10 = models.ImageField(verbose_name=_("Picture 10"), blank=True, null=True, upload_to=article_img_path)
    img_11 = models.ImageField(verbose_name=_("Picture 11"), blank=True, null=True, upload_to=article_img_path)
    img_12 = models.ImageField(verbose_name=_("Picture 12"), blank=True, null=True, upload_to=article_img_path)
    img_13 = models.ImageField(verbose_name=_("Picture 13"), blank=True, null=True, upload_to=article_img_path)
    img_14 = models.ImageField(verbose_name=_("Picture 14"), blank=True, null=True, upload_to=article_img_path)
    img_15 = models.ImageField(verbose_name=_("Picture 15"), blank=True, null=True, upload_to=article_img_path)
    img_16 = models.ImageField(verbose_name=_("Picture 16"), blank=True, null=True, upload_to=article_img_path)
    img_17 = models.ImageField(verbose_name=_("Picture 17"), blank=True, null=True, upload_to=article_img_path)
    img_18 = models.ImageField(verbose_name=_("Picture 18"), blank=True, null=True, upload_to=article_img_path)
    img_19 = models.ImageField(verbose_name=_("Picture 19"), blank=True, null=True, upload_to=article_img_path)
    img_20 = models.ImageField(verbose_name=_("Picture 20"), blank=True, null=True, upload_to=article_img_path)
    img_21 = models.ImageField(verbose_name=_("Picture 21"), blank=True, null=True, upload_to=article_img_path)
    img_22 = models.ImageField(verbose_name=_("Picture 22"), blank=True, null=True, upload_to=article_img_path)
    img_23 = models.ImageField(verbose_name=_("Picture 23"), blank=True, null=True, upload_to=article_img_path)
    img_24 = models.ImageField(verbose_name=_("Picture 24"), blank=True, null=True, upload_to=article_img_path)
    img_25 = models.ImageField(verbose_name=_("Picture 25"), blank=True, null=True, upload_to=article_img_path)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Author"), blank=True, null=True)
    tags = TaggableManager()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created", editable=False)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Edited", editable=False)
    deleted = models.BooleanField(default=False)

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
    model = models.CharField(max_length=256, verbose_name=_("Device model"))
    size = models.CharField(max_length=256, verbose_name=_("Dimensions"))
    power = models.CharField(max_length=256, verbose_name=_("Power supply"))
    protocols = models.ManyToManyField('Protocol', verbose_name=_("Supported protocols"), blank=True)
    temperature = models.CharField(max_length=256, verbose_name=_("Operating temperature"))
    platforms = models.ManyToManyField(Platform, verbose_name=_("Platforms"), blank=True)
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


class Scenario(models.Model):
    title = models.CharField(max_length=256, verbose_name=_("Title"))
    slug = AutoSlugField(populate_from="title", verbose_name=_("URL"))
    text = models.TextField(verbose_name=_("Text"), blank=True)
    description = models.TextField(verbose_name=_("Description"), blank=True)
    main_img = models.ImageField(verbose_name=_("Main image"), blank=True, null=True, upload_to=scenarios_img_path)
    img_1 = models.ImageField(verbose_name=_("Image 1"), blank=True, null=True, upload_to=scenarios_img_path)
    img_2 = models.ImageField(verbose_name=_("Image 2"), blank=True, null=True, upload_to=scenarios_img_path)
    img_3 = models.ImageField(verbose_name=_("Image 3"), blank=True, null=True, upload_to=scenarios_img_path)
    img_4 = models.ImageField(verbose_name=_("Image 4"), blank=True, null=True, upload_to=scenarios_img_path)
    img_5 = models.ImageField(verbose_name=_("Image 5"), blank=True, null=True, upload_to=scenarios_img_path)
    img_6 = models.ImageField(verbose_name=_("Image 6"), blank=True, null=True, upload_to=scenarios_img_path)
    img_7 = models.ImageField(verbose_name=_("Image 7"), blank=True, null=True, upload_to=scenarios_img_path)
    img_8 = models.ImageField(verbose_name=_("Image 8"), blank=True, null=True, upload_to=scenarios_img_path)
    img_9 = models.ImageField(verbose_name=_("Image 9"), blank=True, null=True, upload_to=scenarios_img_path)
    img_10 = models.ImageField(verbose_name=_("Image 10"), blank=True, null=True, upload_to=scenarios_img_path)
    img_11 = models.ImageField(verbose_name=_("Image 11"), blank=True, null=True, upload_to=scenarios_img_path)
    img_12 = models.ImageField(verbose_name=_("Image 12"), blank=True, null=True, upload_to=scenarios_img_path)
    img_13 = models.ImageField(verbose_name=_("Image 13"), blank=True, null=True, upload_to=scenarios_img_path)
    img_14 = models.ImageField(verbose_name=_("Image 14"), blank=True, null=True, upload_to=scenarios_img_path)
    img_15 = models.ImageField(verbose_name=_("Image 15"), blank=True, null=True, upload_to=scenarios_img_path)
    img_16 = models.ImageField(verbose_name=_("Image 16"), blank=True, null=True, upload_to=scenarios_img_path)
    img_17 = models.ImageField(verbose_name=_("Image 17"), blank=True, null=True, upload_to=scenarios_img_path)
    img_18 = models.ImageField(verbose_name=_("Image 18"), blank=True, null=True, upload_to=scenarios_img_path)
    img_19 = models.ImageField(verbose_name=_("Image 19"), blank=True, null=True, upload_to=scenarios_img_path)
    img_20 = models.ImageField(verbose_name=_("Image 20"), blank=True, null=True, upload_to=scenarios_img_path)
    img_21 = models.ImageField(verbose_name=_("Image 21"), blank=True, null=True, upload_to=scenarios_img_path)
    img_22 = models.ImageField(verbose_name=_("Image 22"), blank=True, null=True, upload_to=scenarios_img_path)
    img_23 = models.ImageField(verbose_name=_("Image 23"), blank=True, null=True, upload_to=scenarios_img_path)
    img_24 = models.ImageField(verbose_name=_("Image 24"), blank=True, null=True, upload_to=scenarios_img_path)
    scheme = models.ImageField(verbose_name=_("Scheme"), blank=True, null=True, upload_to=scenarios_img_path)
    devices = models.ManyToManyField(Device)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Author"), blank=True, null=True)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, blank=True, null=True)
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, blank=True, null=True)
    tags = TaggableManager()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"), editable=False)
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"), editable=False)
    deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.pk} {self.title}"

    def delete(self, *args):
        self.deleted = True
        self.save()

    class Meta:
        verbose_name = _("Scenario")
        verbose_name_plural = _("Scenarios")
        ordering = ["title"]

    def next(self):
        return self.get_next_by_created_at()

    def pre(self):
        return self.get_previous_by_created_at()
    
    def get_absolute_url(self):
        return f'/mainapp/scenarios/{self.slug}'
    
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
    
    def get_similar_scenarios(self):
        '''
        Функция ищет похожие сценарии устройства которых такие же как и заданного сценария.
        Возвращает список сценариев которые можно реализовать из этих же устройств или 
        сценариев где нужно докупить несколько устройств
        '''
        
        similar_scenarios = []
        devices = set(self.devices.all())
        all_scenarios = Scenario.objects.all() # Все сценарии в базе
        
        for scenario in all_scenarios: # Проходим по всем сценариям и проверяем утсройства
            scenario_devices = set(scenario.devices.all())
            if devices <= scenario_devices and self.id != scenario.id: # <= означает вхождение подмножества в множество
                similar_scenarios.append(scenario)
            elif scenario_devices <= devices and self.id != scenario.id:
                similar_scenarios.append(scenario)
        return similar_scenarios
    

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