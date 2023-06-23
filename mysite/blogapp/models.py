from django.db import models
from django.urls import reverse

# Create your models here.

class Author(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(null=False, blank=True)


class Category(models.Model):
    name = models.CharField(max_length=40)


class Tag(models.Model):
    name = models.CharField(max_length=20)


class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(null=False, blank=True)
    pub_date = models.DateTimeField(auto_now_add=True, null=False, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, related_name="articles")


class NewArticle(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)


    def get_absolute_url(self):
        return reverse("blogapp:newarticle", kwargs={"pk": self.pk})