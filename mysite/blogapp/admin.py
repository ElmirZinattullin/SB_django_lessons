from django.contrib import admin

from .models import NewArticle


@admin.register(NewArticle)
class NewArticleAdmin(admin.ModelAdmin):
    list_display = 'id', 'title', 'body', 'published_at',