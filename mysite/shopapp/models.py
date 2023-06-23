from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

def get_sentinel_user():
    return get_user_model().objects.get_or_create(id=1)[0]


def product_preview_directory_path(instanse:"Product", filename: str) -> str:
    return "products/product_{pk}/preview/{filename}".format(
        pk=instanse.pk,
        filename=filename
    )


class Product(models.Model):
    """
    Модель Product представляет товар,
    который можно продавать в магазине

    Заказы тут: :model: `shopapp.Order`
    """
    class Meta:
        ordering = ["name"]
        # db_table = "tech_products"
        # verbose_name_plural = "products"
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
    created_by = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user), null=True)
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(null=False, blank=True, db_index=True)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    discount = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)
    preview = models.ImageField(null=True, blank=True, upload_to=product_preview_directory_path)

    @property
    def description_short(self) -> str:
        if len(self.description) < 48:
            return self.description
        return self.description[:48] + '...'

    def __str__(self) -> str:
        return f"Product (pk={self.pk}, name={self.name!r})"

    def get_absolute_url(self):
        return reverse("shopapp:product_details", kwargs={"pk": self.pk})


class Order(models.Model):
    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    delivery_address = models.TextField(null=True, blank=True)
    promocode = models.CharField(max_length=20, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    products = models.ManyToManyField(Product, related_name="orders")
    receipt = models.FileField(null=True, upload_to='orders/receipts')


