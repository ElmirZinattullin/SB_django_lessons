from csv import DictReader
from io import TextIOWrapper

from shopapp.models import Product, Order


def save_csv_products(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )
    reader = DictReader(csv_file)

    products = [Product(**row) for row in reader]

    Product.objects.bulk_create(products)
    return products


def save_csv_orders(file, encoding, user):
    # csv_file = TextIOWrapper(
    #     file,
    #     encoding=encoding,
    # )
    # reader = DictReader(csv_file)
    # orders = [Order(**row) for row in reader]
    # for order in orders:
    #     if not order.user_id:
    #         order.user = user
    # Order.objects.bulk_create(orders)
    # return orders
    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )
    reader = DictReader(csv_file)
    orders = list()
    for row in reader:
        products = row.pop('products')
        new_order = Order(**row)
        product_list = [int(pk) for pk in products.split(',')]
        if not new_order.user_id:
            new_order.user = user
        new_order.save()
        for product in product_list:
            new_order.products.add(product)
        new_order.save()
        orders.append(new_order)
    return orders
