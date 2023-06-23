from django.contrib.sitemaps import Sitemap

from .models import NewArticle


class BlogSiteMap(Sitemap):
    changefreq = 'never'
    priority = 0.5

    def items(self):
        return NewArticle.objects.filter(published_at__isnull=False).order_by('-published_at')


    def lastmod(self, object:NewArticle):
        return object.published_at
