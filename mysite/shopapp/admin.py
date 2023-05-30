from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import Product, Order
from .admin_mixins import ExportAsCVSMixin


# Register your models here.


class OrderInLine(admin.TabularInline):
    model = Product.orders.through


@admin.action(description="Archive products")
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True)


@admin.action(description="Unarchive products")
def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCVSMixin):
    actions = [mark_archived, mark_unarchived, "export_csv"]
    inlines = [OrderInLine, ]
    list_display = "pk", "name", 'description_short', "price", "discount", "archived"
    list_display_links = "pk", "name",
    ordering = "pk", "price"
    search_fields = "name", "price", "pk"
    fieldsets = [
        (None, {
            "fields": ("name", "description")
        }),
        ("Price opions", {
            "fields": ("price", "discount")
        }),
        ("Extra options", {
            "fields": ("archived", ),
            "classes": ("collapse", ),
            "description": "Extra options. Field 'archived' is for soft delete",
        })
    ]


class ProductInLine(admin.StackedInline):
    model = Order.products.through


# admin.site.register(Product, ProductAdmin)
@admin.register(Order)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductInLine, ]
    list_display = "pk", "delivery_address", "promocode", "created_at", "user_verbose"
    list_display_links = "pk", "delivery_address",

    def get_queryset(self, request):
        return Order.objects.select_related("user").prefetch_related("products")

    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username


