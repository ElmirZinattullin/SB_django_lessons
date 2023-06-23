from django.contrib.auth.views import LoginView
from django.urls import path

from .views import ArticlesListView, NewArticlesListView, NewArticlesDetailView, LatestNewArticlesFeed

app_name = "blogapp"

urlpatterns = [
    path('articles/', ArticlesListView.as_view(), name='articles_list'),
    path('newarticles/', NewArticlesListView.as_view(), name='newarticles_list'),
    path('newarticles/<int:pk>/', NewArticlesDetailView.as_view(), name='newarticle'),
    path('newarticles/latest/feed/', LatestNewArticlesFeed(), name='newarticles-feed')
]
