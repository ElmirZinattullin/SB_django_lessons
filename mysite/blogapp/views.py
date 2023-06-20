from django.shortcuts import render
from django.views.generic import ListView

from .models import Article, Category, Tag, Author

# Create your views here.

class ArticlesListView(ListView):
    template_name = "blogapp/article_list.html"
    model = Article
    queryset = Article.objects.defer('content').all().select_related('category', 'author').prefetch_related('tags')
    context_object_name = 'articles'
