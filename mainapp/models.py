from pathlib import Path

from django.contrib.auth import get_user_model
from django.db import models


def device_foto_path(instance, filename):
    # file will be uploaded to
    #   MEDIA_ROOT / devices_foto / <model> / <filename>
    suff = Path(filename).suffix
    return "devices_foto/{0}/{1}".format(instance.model, filename)


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
    description = models.TextField(blank=True, null=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Категория статьи"
        verbose_name_plural = "Категории статей"
        ordering = ["title"]

    def __str__(self) -> str:
        return f"{self.title}"


class DeviceCategory(models.Model):
    title = models.CharField(max_length=256, verbose_name="Название")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Категория устройства"
        verbose_name_plural = "Категории устройств"
        ordering = ["title"]

    def __str__(self) -> str:
        return f"{self.title}"


class Articles(models.Model):
    title = models.CharField(max_length=256, verbose_name="Название")
    category = models.ForeignKey(
        ArticleCategory, verbose_name="Категория", on_delete=models.CASCADE, related_name="articles"
    )
    slug = models.SlugField(verbose_name="URL", unique=True, blank=True, null=True)
    preambule = models.TextField(verbose_name="Краткое описание", blank=True)
    text = models.TextField(verbose_name="Текст", blank=True)
    images = models.ImageField(verbose_name="Изображение", blank=True, null=True, upload_to="articles_img/")
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


class Devices(models.Model):
    category = models.ForeignKey(
        DeviceCategory, verbose_name="Категория", on_delete=models.CASCADE, related_name="devices"
    )
    title = models.CharField(max_length=256, verbose_name="Название")
    slug = models.SlugField(verbose_name="URL", max_length=200, unique=True, blank=True, null=True)
    description = models.TextField(verbose_name="Описание", blank=True)
    foto1 = models.ImageField(verbose_name="Фото устройства_1", blank=True, null=True, upload_to=device_foto_path)

    model = models.CharField(max_length=256, verbose_name="Модель устройства")
    size = models.CharField(max_length=256, verbose_name="Размеры")
    power = models.CharField(max_length=256, verbose_name="Питание")
    protocol = models.CharField(max_length=256, verbose_name="Поддерживаемые протоколы передачи")
    temperature = models.CharField(max_length=256, verbose_name="Рабочие температуры")
    platforms = models.ManyToManyField(Platforms)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name="Автор", blank=True, null=True)
    set = models.CharField(max_length=256, verbose_name="Комплект")
    link_to_buy = models.CharField(max_length=256, verbose_name="Ссылка для покупки")
    deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.pk} {self.title}"

    def delete(self, *args):
        self.deleted = True
        self.save()

    class Meta:
        verbose_name = "Устройство"
        verbose_name_plural = "Устройства"
        ordering = ["title"]


class Scenarios(models.Model):
    title = models.CharField(max_length=256, verbose_name="Название")
    text = models.TextField(verbose_name="Текст", blank=True)
    description = models.TextField(verbose_name="Описание", blank=True)
    images = models.ImageField(verbose_name="Изображение", blank=True, null=True, upload_to="scenarios_img/")
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
