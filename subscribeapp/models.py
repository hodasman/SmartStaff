from django.db import models


class Subscribers(models.Model):
    '''Подписка по email'''
    email = models.EmailField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__self(self):
        return self.email