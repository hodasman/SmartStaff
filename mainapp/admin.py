from django.contrib import admin

from authapp import models as authapp_models
from mainapp import models as mainapp_models

admin.site.register(mainapp_models.Scenarios)
admin.site.register(mainapp_models.Devices)
admin.site.register(mainapp_models.Articles)
admin.site.register(mainapp_models.Platforms)
admin.site.register(authapp_models.User)
admin.site.register(mainapp_models.ArticleCategory)
admin.site.register(mainapp_models.DeviceCategory)
