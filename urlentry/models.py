from django.db import models


class UrlEntry(models.Model):
    def __str__(self):
        return self.short_url_code

    original_url = models.CharField(max_length=1000)
    short_url_code = models.CharField(max_length=10)
