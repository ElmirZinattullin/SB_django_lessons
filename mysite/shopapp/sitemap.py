from django.contrib.sitemaps import Sitemap

from .models import Product


class ShopSiteMap(Sitemap):
    changefreq = 'never'
    priority = 0.4

    def items(self):
        return Product.objects.filter(archived=False).order_by('-created_at')


    def lastmod(self, object:Product):
        return object.created_at
