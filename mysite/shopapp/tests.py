from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse

from shopapp.models import Order, Product
from shopapp.utils import add_two_numbers


# class AddTwoNumbersTestCase(TestCase):
#     def test_add_two_numbers(self):
#         result = add_two_numbers(2, 3)
#         print(result)
#         self.assertEquals(result, 5)
#         print(self.assertEquals(result, 5))

#
# if __name__ == "__main__":
#     abs = AddTwoNumbersTestCase()
#     abs.test_add_two_numbers()
class ProductCreateViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='Bob_test', password="qwerty")

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_create_product(self):
        response = self.client.post(
            reverse('shopapp:product_create'),
            {'name': "Table", 'price': "123.45", 'description': "A god table", 'discount': "14"}
        )
        # print(self.user)
        self.assertRedirects(response, reverse("shopapp:products_list"))


class OrderDetailViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='Bob_test', password="qwerty")
        permisssion = Permission.objects.get_by_natural_key('view_order', 'shopapp', 'order')
        cls.user.user_permissions.add(permisssion)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)
        self.product = Product.objects.create(name='Test_product', description='test', price=100, discount=10)
        self.test_order = Order.objects.create(delivery_address='address test', promocode='TEST', user=self.user)
        self.test_order.products.add(self.product)

    def tearDown(self) -> None:
        self.product.delete()
        self.test_order.delete()

    def test_order_details_view(self):
        pk = self.test_order.pk
        response = self.client.get(
            reverse('shopapp:order_details', kwargs={'pk': pk})
        )
        self.assertContains(response, 'address test')
        self.assertContains(response, 'TEST')
        self.assertEquals(response.context.get("object").pk, pk)


class OrdersExportTestCase(TestCase):
    fixtures = ['products-fixtures.json', 'orders-fixtures.json', 'users-fixtures.json']

    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='Gosha_test', password='thisismypassword')
        cls.user.is_staff = True
        cls.user.save()

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_get_orders_export(self):
        response = self.client.get(reverse('shopapp:orders_export'))
        self.assertEquals(response.status_code, 200)
        orders = Order.objects.order_by("pk").all()
        order_list = [{
            'ID': order.pk,
            'address': order.delivery_address,
            'promocode': order.promocode,
            'user_ID': order.user.pk,
            'products_id': [product.pk for product in order.products.filter(orders=order)]}
            for order in orders]
        expected_data = order_list
        orders_data = response.json()
        self.assertEquals(
            orders_data['orders'],
            expected_data
        )
