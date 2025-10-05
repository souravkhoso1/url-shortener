from django.contrib import admin
from .models import ShortenedURL

@admin.register(ShortenedURL)
class ShortenedURLAdmin(admin.ModelAdmin):
    list_display = ('short_code', 'original_url', 'clicks', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('short_code', 'original_url')
    readonly_fields = ('created_at', 'clicks')
    ordering = ('-created_at',)