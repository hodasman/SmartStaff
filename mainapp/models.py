from autoslug import AutoSlugField
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q


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


class Platforms(models.Model):
    title = models.CharField(max_length=256, verbose_name="Название")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Платформа"
        verbose_name_plural = "Платформы"
        ordering = ["title"]

    def __str__(self) -> str:
        return f"{self.title}"


class ArticleCategory(models.Model):
    title = models.CharField(max_length=256, verbose_name="Название")
    slug = AutoSlugField(populate_from="title")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Категория статьи"
        verbose_name_plural = "Категории статей"
        ordering = ["title"]

    def __str__(self) -> str:
        return f"{self.title}"
    
    def qty_articles_in_category(self):
        qty = len(Articles.objects.filter(category__slug=self.slug, deleted=False))
        return qty


class DeviceCategory(models.Model):
    title = models.CharField(max_length=256, verbose_name="Название")
    slug = AutoSlugField(populate_from="title")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Категория устройства"
        verbose_name_plural = "Категории устройств"
        ordering = ["title"]

    def __str__(self) -> str:
        return f"{self.title}"


class ObjectManager(models.Manager):
    use_for_related_fields = True
 
    def search(self, query=None):
        qs = self.get_queryset()
        if query:
            or_lookup = (Q(title__icontains=query) | Q(text__icontains=query))
            qs = qs.filter(or_lookup)
 
        return qs


class Articles(models.Model):
    objects = ObjectManager()
    title = models.CharField(max_length=256, verbose_name="Название")
    category = models.ForeignKey(
        ArticleCategory, verbose_name="Категория", on_delete=models.CASCADE, related_name="articles"
    )
    slug = AutoSlugField(populate_from="title", verbose_name="URL")
    preambule = models.TextField(verbose_name="Краткое описание", blank=True)
    text = models.TextField(verbose_name="Текст", blank=True)
    main_img = models.ImageField(verbose_name="Заглавная картинка", blank=True, null=True, upload_to=article_img_path)
    img_1 = models.ImageField(verbose_name="Картинка_1", blank=True, null=True, upload_to=article_img_path)
    img_2 = models.ImageField(verbose_name="Картинка_2", blank=True, null=True, upload_to=article_img_path)
    img_3 = models.ImageField(verbose_name="Картинка_3", blank=True, null=True, upload_to=article_img_path)
    img_4 = models.ImageField(verbose_name="Картинка_4", blank=True, null=True, upload_to=article_img_path)
    img_5 = models.ImageField(verbose_name="Картинка_5", blank=True, null=True, upload_to=article_img_path)
    img_6 = models.ImageField(verbose_name="Картинка_6", blank=True, null=True, upload_to=article_img_path)
    img_7 = models.ImageField(verbose_name="Картинка_7", blank=True, null=True, upload_to=article_img_path)
    img_8 = models.ImageField(verbose_name="Картинка_8", blank=True, null=True, upload_to=article_img_path)
    img_9 = models.ImageField(verbose_name="Картинка_9", blank=True, null=True, upload_to=article_img_path)
    img_10 = models.ImageField(verbose_name="Картинка_10", blank=True, null=True, upload_to=article_img_path)
    img_11 = models.ImageField(verbose_name="Картинка_11", blank=True, null=True, upload_to=article_img_path)
    img_12 = models.ImageField(verbose_name="Картинка_12", blank=True, null=True, upload_to=article_img_path)
    img_13 = models.ImageField(verbose_name="Картинка_13", blank=True, null=True, upload_to=article_img_path)
    img_14 = models.ImageField(verbose_name="Картинка_14", blank=True, null=True, upload_to=article_img_path)
    img_15 = models.ImageField(verbose_name="Картинка_15", blank=True, null=True, upload_to=article_img_path)
    img_16 = models.ImageField(verbose_name="Картинка_16", blank=True, null=True, upload_to=article_img_path)
    img_17 = models.ImageField(verbose_name="Картинка_17", blank=True, null=True, upload_to=article_img_path)
    img_18 = models.ImageField(verbose_name="Картинка_18", blank=True, null=True, upload_to=article_img_path)
    img_19 = models.ImageField(verbose_name="Картинка_19", blank=True, null=True, upload_to=article_img_path)
    img_20 = models.ImageField(verbose_name="Картинка_20", blank=True, null=True, upload_to=article_img_path)
    img_21 = models.ImageField(verbose_name="Картинка_21", blank=True, null=True, upload_to=article_img_path)
    img_22 = models.ImageField(verbose_name="Картинка_22", blank=True, null=True, upload_to=article_img_path)
    img_23 = models.ImageField(verbose_name="Картинка_23", blank=True, null=True, upload_to=article_img_path)
    img_24 = models.ImageField(verbose_name="Картинка_24", blank=True, null=True, upload_to=article_img_path)
    img_25 = models.ImageField(verbose_name="Картинка_25", blank=True, null=True, upload_to=article_img_path)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name="Автор", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created", editable=False)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Edited", editable=False)
    deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.pk} {self.title}"

    def delete(self, *args):
        self.deleted = True
        self.save()

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
        ordering = ["title"]
    
    def get_absolute_url(self):
        return f'/mainapp/articles/{self.slug}'


class Devices(models.Model):
    category = models.ForeignKey(
        DeviceCategory, verbose_name="Категория", on_delete=models.CASCADE, related_name="devices"
    )
    title = models.CharField(max_length=256, verbose_name="Название")
    slug = AutoSlugField(populate_from="title", verbose_name="URL")
    description = models.TextField(verbose_name="Описание", blank=True)
    icon = models.ImageField(verbose_name="Иконка_устройства", blank=True, null=True, upload_to=device_foto_path)
    foto1 = models.ImageField(verbose_name="Фото устройства_1", blank=True, null=True, upload_to=device_foto_path)
    foto2 = models.ImageField(verbose_name="Фото устройства_2", blank=True, null=True, upload_to=device_foto_path)
    foto3 = models.ImageField(verbose_name="Фото устройства_3", blank=True, null=True, upload_to=device_foto_path)
    foto4 = models.ImageField(verbose_name="Фото устройства_4", blank=True, null=True, upload_to=device_foto_path)
    model = models.CharField(max_length=256, verbose_name="Модель устройства")
    size = models.CharField(max_length=256, verbose_name="Размеры")
    power = models.CharField(max_length=256, verbose_name="Питание")
    protocol = models.CharField(max_length=256, verbose_name="Поддерживаемые протоколы передачи")
    temperature = models.CharField(max_length=256, verbose_name="Рабочие температуры")
    platforms = models.ManyToManyField(Platforms, verbose_name="Платформы", blank=True)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name="Автор", blank=True, null=True)
    set = models.CharField(max_length=256, verbose_name="Комплект")
    link_to_buy = models.CharField(max_length=256, verbose_name="Ссылка для покупки")
    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(verbose_name="Создан", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Обновлен", auto_now=True)

    def __str__(self) -> str:
        return f"{self.title}"

    def delete(self, *args):
        self.deleted = True
        self.save()

    class Meta:
        verbose_name = "Устройство"
        verbose_name_plural = "Устройства"
        ordering = ["title"]



class Scenarios(models.Model):
    objects = ObjectManager()
    title = models.CharField(max_length=256, verbose_name="Название")
    slug = AutoSlugField(populate_from="title", verbose_name="URL")
    text = models.TextField(verbose_name="Текст", blank=True)
    description = models.TextField(verbose_name="Описание", blank=True)
    main_img = models.ImageField(verbose_name="Заглавная картинка", blank=True, null=True, upload_to=scenarios_img_path)
    img_1 = models.ImageField(verbose_name="Картинка_1", blank=True, null=True, upload_to=scenarios_img_path)
    img_2 = models.ImageField(verbose_name="Картинка_2", blank=True, null=True, upload_to=scenarios_img_path)
    img_3 = models.ImageField(verbose_name="Картинка_3", blank=True, null=True, upload_to=scenarios_img_path)
    img_4 = models.ImageField(verbose_name="Картинка_4", blank=True, null=True, upload_to=scenarios_img_path)
    img_5 = models.ImageField(verbose_name="Картинка_5", blank=True, null=True, upload_to=scenarios_img_path)
    img_6 = models.ImageField(verbose_name="Картинка_6", blank=True, null=True, upload_to=scenarios_img_path)
    img_7 = models.ImageField(verbose_name="Картинка_7", blank=True, null=True, upload_to=scenarios_img_path)
    img_8 = models.ImageField(verbose_name="Картинка_8", blank=True, null=True, upload_to=scenarios_img_path)
    img_9 = models.ImageField(verbose_name="Картинка_9", blank=True, null=True, upload_to=scenarios_img_path)
    img_10 = models.ImageField(verbose_name="Картинка_10", blank=True, null=True, upload_to=scenarios_img_path)
    img_11 = models.ImageField(verbose_name="Картинка_11", blank=True, null=True, upload_to=scenarios_img_path)
    img_12 = models.ImageField(verbose_name="Картинка_12", blank=True, null=True, upload_to=scenarios_img_path)
    img_13 = models.ImageField(verbose_name="Картинка_13", blank=True, null=True, upload_to=scenarios_img_path)
    img_14 = models.ImageField(verbose_name="Картинка_14", blank=True, null=True, upload_to=scenarios_img_path)
    img_15 = models.ImageField(verbose_name="Картинка_15", blank=True, null=True, upload_to=scenarios_img_path)
    img_16 = models.ImageField(verbose_name="Картинка_16", blank=True, null=True, upload_to=scenarios_img_path)
    img_17 = models.ImageField(verbose_name="Картинка_17", blank=True, null=True, upload_to=scenarios_img_path)
    img_18 = models.ImageField(verbose_name="Картинка_18", blank=True, null=True, upload_to=scenarios_img_path)
    img_19 = models.ImageField(verbose_name="Картинка_19", blank=True, null=True, upload_to=scenarios_img_path)
    img_20 = models.ImageField(verbose_name="Картинка_20", blank=True, null=True, upload_to=scenarios_img_path)
    img_21 = models.ImageField(verbose_name="Картинка_21", blank=True, null=True, upload_to=scenarios_img_path)
    img_22 = models.ImageField(verbose_name="Картинка_22", blank=True, null=True, upload_to=scenarios_img_path)
    img_23 = models.ImageField(verbose_name="Картинка_23", blank=True, null=True, upload_to=scenarios_img_path)
    img_24 = models.ImageField(verbose_name="Картинка_24", blank=True, null=True, upload_to=scenarios_img_path)
    img_25 = models.ImageField(verbose_name="Картинка_25", blank=True, null=True, upload_to=scenarios_img_path)
    devices = models.ManyToManyField(Devices)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name="Автор", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания", editable=False)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата редактирования", editable=False)
    deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.pk} {self.title}"

    def delete(self, *args):
        self.deleted = True
        self.save()

    class Meta:
        verbose_name = "Сценарий"
        verbose_name_plural = "Сценарии"
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
    

class RatingStar(models.Model):
    '''Звезда рейтинга(1-5)'''
    value  = models.SmallIntegerField("Значение", default=0)

    def __str__(self) -> str:
        return f'{self.value}'

    class Meta:
        verbose_name = "Звезда рейтинга"
        verbose_name_plural = "Звезды рейтинга"
        ordering = ["-value"]


class Rating(models.Model):
    '''Рейтинг'''
    ip = models.CharField('IP Адрес', max_length=15)
    star = models.ForeignKey(RatingStar, on_delete=models.CASCADE, verbose_name="Звезда")
    scenario = models.ForeignKey(Scenarios, on_delete=models.CASCADE, verbose_name="Сценарий",)

    def __str__(self) -> str:
        return f'{self.scenario} - {self.star}'
    
    class Meta:
        verbose_name = "Рейтинг"
        verbose_name_plural = "Рейтинги"
        

class ArticleComment(models.Model):
    class Meta:
        db_table = "article_comments"
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    article = models.ForeignKey(Articles, on_delete=models.CASCADE, verbose_name="Статья")
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name="Автор комментария")
    content = models.TextField(verbose_name="Текст")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата комментария", editable=False)


class ScenarioComment(models.Model):
    class Meta:
        db_table = "scenario_comments"
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    scenario = models.ForeignKey(Scenarios, on_delete=models.CASCADE, verbose_name="Статья")
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name="Автор комментария")
    content = models.TextField(verbose_name="Текст")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата комментария", editable=False)