from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib.messages import constants

from .common import save_csv_products, save_csv_orders
from .models import Product, Order
from .admin_mixins import ExportAsCVSMixin
from .forms import CSVImportForm


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
    change_list_template = "shopapp/products_change_list.html"
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

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportForm()
            context = {
                "form": form,
            }
            return render(request, "admin/csv-form.html", context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                "from": form,
            }
            return render(request, "admin/csv-form.html", context, status=400)
        save_csv_products(
            file=form.files["csv_file"].file,
            encoding=request.encoding,
        )
        self.message_user(request, "Data from CSV was imported")
        return redirect('..')

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path("import-products-csv/", self.import_csv, name="import-products-csv")
        ]
        return new_urls + urls


class ProductInLine(admin.StackedInline):
    model = Order.products.through


# admin.site.register(Product, ProductAdmin)
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    change_list_template = 'shopapp/orders_changelist.html'

    inlines = [ProductInLine, ]
    list_display = "pk", "delivery_address", "promocode", "created_at", "user_verbose"
    list_display_links = "pk", "delivery_address",

    def get_queryset(self, request):
        return Order.objects.select_related("user").prefetch_related("products")

    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username


    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportForm()
            context = {
                "form": form,
            }
            return render(request, "admin/csv-form.html", context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                "from": form,
            }
            return render(request, "admin/csv-form.html", context, status=400)
        user=request.user
        try:
            save_csv_orders(
                file=form.files["csv_file"].file,
                encoding=request.encoding,
                user=request.user
            )
            self.message_user(request, "Data from CSV was imported")
        except TypeError as error:
            self.message_user(request, f"ERROR. Data from CSV was not imported. MSG: {error}", level=constants.ERROR)
        return redirect('..')

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path("import-orders-csv/", self.import_csv, name="import-orders-csv")
        ]
        return new_urls + urls



