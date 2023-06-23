"""
В этом модуле лежат различные наборы представлений.

 Различные view для интернет-магазина: по товаром, заказам и т.д.
"""

import time
import logging
from timeit import default_timer
from csv import DictWriter

from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.syndication.views import Feed
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.request import Request
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .forms import GroupForm
from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer
from .common import save_csv_products


log = logging.getLogger(__name__)

@extend_schema(description="Product views CRUD")
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product
    Полный CRUD для сущностей товаров
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['name', 'description',]
    filterset_fields = [
        'name',
        'description',
        'price',
        'discount',
        'archived',
    ]
    ordering_fields = [
        "name",
        "price",
        "discount",
    ]
    @extend_schema(
        summary="Get one product by ID",
        description="Retrieves **product**, returns 404 if not found",
        responses= {
            200: ProductSerializer,
            404: OpenApiResponse(description="Empty response, product by ID not found"),
                    }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)


    @action(methods=['get'], detail=False)
    def download_csv(self, request: Request):

        response = HttpResponse(content_type="text/csv")
        filename = 'products-export.csv'
        response["Content-Disposition"] = f"attachment; filename={filename}"
        queriset = self.filter_queryset(self.get_queryset())
        fields = [
            'name',
            'description',
            'price',
            'discount',
        ]
        queriset = queriset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queriset:
            writer.writerow(
                {
                    field: getattr(product, field) for field in fields
                }
            )

        return response


    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser])
    def upload_csv(self, request: Request):
        products = save_csv_products(
            request.FILES['file'].file,
            encoding=request.encoding,
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['products', 'user',]
    filterset_fields = [
            "delivery_address",
            "promocode",
            "created_at",
            "user",
            "products",
    ]
    ordering_fields = [
        "user",
        "created_at",
    ]


class ShopIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('Laptop', 1999, 0), ('Desktop', 2999, 20), ('Smartphone', 999, 13),
        ]
        context = {
            "time_running": default_timer(),
            "name": "Elmir",
            "products": products,
            "items": 3

        }
        log.debug("products for shop index: %s", products)
        log.info("Rendering shop index")
        return render(request, 'shopapp/shop-index.html', context=context)


class GroupsListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related('permissions').all(),
        }
        return render(request, 'shopapp/groups-list.html', context=context)

    def post(self, request: HttpRequest):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            time.sleep(1)
        return redirect(request.path)


class ProductDetailView(DetailView):
    template_name = "shopapp/product-details.html"
    model = Product
    context_object_name = 'product'
    extra_context = {'images_amount': [1, 2, 5, 0]}
    # def get(self, request: HttpRequest, pk: int) -> HttpResponse:
    #     product = get_object_or_404(Product, pk=pk)
    #     context ={
    #         "product": product,
    #     }
    #     return render(request, "shopapp/product-details.html", context=context)


class ProductsListView(ListView):
    template_name = "shopapp/products-list.html"
    model = Product
    context_object_name = 'products'
    queryset = Product.objects.filter(archived=False)
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["products"] = Product.objects.all()
    #     return context


# def products_list(request: HttpRequest):
#     context = {
#         "products": Product.objects.all(),
#     }
#     return render(request, 'shopapp/products-list.html', context=context)


class ProductCreateView(CreateView):
# class ProductCreateView(PermissionRequiredMixin, CreateView):
    # permission_required = 'shopapp.add_product'
    model = Product
    fields = 'name', 'price', 'description', 'discount', 'preview'
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        #
        # form1 = form
        # self.object = form.save()
        return super().form_valid(form)

        # return HttpResponseRedirect(self.get_success_url())


class ProductUpdateView(UserPassesTestMixin, UpdateView):

    def test_func(self):
        perms = ('shopapp.change_product', )
        user_has_perms = self.request.user.has_perms(perms)
        access = user_has_perms or (self.get_object().created_by == self.request.user)
        return access


    model = Product
    fields = 'name', 'price', 'description', 'discount', 'preview'
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse(
            "shopapp:product_details",
            kwargs={'pk': self.object.pk}
        )


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class LatestProductsFeed(Feed):
    title = "shop products (latest)"
    description = "updates on changes and addition shop products"
    link = reverse_lazy('shopapp:products_list')

    def items(self):
        return (
            Product.objects
            .filter(archived=False)
            .order_by('-created_at')[:10]
        )

    def item_title(self, item: Product):
        return item.name


    def item_description(self, item: Product):
        return item.description[:100]



class OrdersListView(ListView):
    queryset = (Order.objects.select_related("user").prefetch_related("products"))


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'shopapp.view_order'
    queryset = (Order.objects.select_related("user").prefetch_related("products"))


class OrderCreateView(CreateView):
    # queryset = (Order.objects.select_related("user").prefetch_related("products"))
    model = Order
    fields = 'delivery_address', 'promocode', 'products'
    success_url = reverse_lazy('shopapp:orders_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        #
        # form1 = form
        # self.object = form.save()
        return super().form_valid(form)


class OrderUpdateView(UpdateView):
    model = Order
    fields = 'delivery_address', 'promocode', 'user', 'products'
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse(
            "shopapp:order_details",
            kwargs={'pk': self.object.pk}
        )


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy('shopapp:orders_list')


class OrdersDataExportView(UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request:HttpRequest) -> JsonResponse:
        orders=Order.objects.order_by('pk').all()
        orders_data = list()
        for order in orders:
            product_id_list = list()
            # for product in order.products.get:
            #     product_id_list.append(product.pk)
            products = order.products.filter(orders=order)
            for product in products:
                product_id_list.append(product.pk)
            print(products)
            order_data = {
                    'ID': order.pk,
                    'address': order.delivery_address,
                    'promocode': order.promocode,
                    'user_ID': order.user.pk,
                    'products_id': product_id_list

                }
            orders_data.append(order_data)
        return JsonResponse({'orders': orders_data})


class ProductsDataExportView(View):
    def get(self, request:HttpRequest) -> JsonResponse:
        products = Product.objects.order_by('pk').all()
        products_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": product.price,
            }
            for product in products
        ]
        elem = products_data[0]
        name = elem['name']
        print('name:', name)
        return JsonResponse({"products": products_data})



# def orders_list(request: HttpRequest):
#     context = {
#         "orders": Order.objects.select_related("user").prefetch_related("products").all()
#
#     }
#     return render(request, 'shopapp/order_list.html', context=context)


# def create_product(request: HttpRequest) -> HttpResponse:
#     if request.method == "POST":
#         form = ProductForm(request.POST)
#         if form.is_valid():
#             # name = form.cleaned_data["name"]
#             # price = form.cleaned_data["price"]
#             form.save()
#             # Product.objects.create(**form.cleaned_data)
#             url = reverse("shopapp:products_list")
#             time.sleep(1)
#             return redirect(url)
#     else:
#         form = ProductForm()
#     context = {
#         "form": form,
#     }
#
#     return render(request, "shopapp/create-product.html", context=context)
#

# def create_order(request: HttpRequest) -> HttpResponse:
#     if request.method == "POST":
#         order = Order(user=request.user)
#         form = OrderForm(request.POST, instance=order)
#         if form.is_valid():
#             # #         # name = form.cleaned_data["name"]
#             # #         # price = form.cleaned_data["price"]
#             #         form_with_user = dict(**form.cleaned_data)
#             #         current_user = request.user
#             #         form_with_user['user'] = current_user
#             #         products = form_with_user.pop('products')
#             #         order = Order.objects.create(**form_with_user)
#             #         if products:
#             #             for product in products:
#             #                 order.products.add(product)
#             #             order.save()
#             form.save()
#             url = reverse("shopapp:orders_list")
#             time.sleep(1)
#             return redirect(url)
#     else:
#         form = OrderForm()
#     context = {
#         "form": form,
#     }
#
#     return render(request, "shopapp/order-create.html", context=context)
