from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.contrib.syndication.views import Feed
from django.urls import reverse, reverse_lazy

from .models import Article, Category, Tag, Author, NewArticle

# Create your views here.

class ArticlesListView(ListView):
    template_name = "blogapp/article_list.html"
    model = Article
    queryset = Article.objects.defer('content').all().select_related('category', 'author').prefetch_related('tags')
    context_object_name = 'articles'


class NewArticlesListView(ListView):
    queryset = (
        NewArticle.objects
        .filter(published_at__isnull=False)
        .order_by('-published_at')
    )


class NewArticlesDetailView(DetailView):
    model = NewArticle


class LatestNewArticlesFeed(Feed):
    title = "blog articles (latest)"
    description = "updates on changes and addition blog articles"
    link = reverse_lazy('blogapp:newarticles_list')

    def items(self):
        return (
            NewArticle.objects
            .filter(published_at__isnull=False)
            .order_by('-published_at')[:5]
        )

    def item_title(self, item: NewArticle):
        return item.title


    def item_description(self, item: NewArticle):
        return item.body[:200]


    # def item_link(self, item: NewArticle):
    #     return reverse("blogapp:newarticle", kwargs={"pk": item.pk})