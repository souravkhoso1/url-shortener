# shortener/models.py
from django.db import models
import string
import random


class ShortenedURL(models.Model):
    original_url = models.URLField(max_length=2048)
    short_code = models.CharField(max_length=10, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    clicks = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.short_code} -> {self.original_url}"

    @staticmethod
    def generate_short_code(length=6):
        chars = string.ascii_letters + string.digits
        while True:
            code = ''.join(random.choice(chars) for _ in range(length))
            if not ShortenedURL.objects.filter(short_code=code).exists():
                return code