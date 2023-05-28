from timeit import default_timer

from django.http import HttpResponse, HttpRequest
from django.shortcuts import render

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