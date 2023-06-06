import time
from timeit import default_timer

from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect, reverse

from .forms import ProductForm, OrderForm
from .models import Product, Order

def shop_index(request: HttpRequest):
    # print(request.path)
    # print(request.method)
    # print(request.headers)
    # return HttpResponse('<h1>Hello World!</h1>')
    products = [
        ('Laptop', 1999, 0), ('Desktop', 2999, 20), ('Smartphone', 999, 13),
    ]
    context = {
        "time_running": default_timer(),
        "name": "Elmir",
        "products": products

    }
    return render(request, 'shopapp/shop-index.html', context=context)


def groups_list(request: HttpRequest):
    context = {
        "groups": Group.objects.prefetch_related('permissions').all(),
    }
    return render(request, 'shopapp/groups-list.html', context=context)


def products_list(request: HttpRequest):
    context = {
        "products": Product.objects.all(),
    }
    return render(request, 'shopapp/products-list.html', context=context)


def orders_list(request: HttpRequest):
    context = {
        "orders": Order.objects.select_related("user").prefetch_related("products").all()

    }
    return render(request, 'shopapp/orders-list.html', context=context)


def create_product(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            # name = form.cleaned_data["name"]
            # price = form.cleaned_data["price"]
            form.save()
            # Product.objects.create(**form.cleaned_data)
            url = reverse("shopapp:products_list")
            time.sleep(1)
            return redirect(url)
    else:
        form = ProductForm()
    context = {
        "form": form,
    }

    return render(request, "shopapp/create-product.html", context=context)


def create_order(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
    #         # name = form.cleaned_data["name"]
    #         # price = form.cleaned_data["price"]
            form_with_user = dict(**form.cleaned_data)
            current_user = request.user
            form_with_user['user'] = current_user
            products = form_with_user.pop('products')
            order = Order.objects.create(**form_with_user)
            if products:
                for product in products:
                    order.products.add(product)
                order.save()
            url = reverse("shopapp:orders_list")
            time.sleep(1)
            return redirect(url)
    else:
        form = OrderForm()
    context = {
        "form": form,
    }

    return render(request, "shopapp/order-create.html", context=context)
