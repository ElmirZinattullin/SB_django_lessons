from django.core.management import BaseCommand
from django.db import transaction

from blogapp.models import Category


class Command(BaseCommand):
    @transaction.atomic()
    def handle(self, *args, **options):
        self.stdout.write("Create category")

        categories = [
            'love',
            'nature',
            'war',
            'another',
        ]
        for category in categories:
            new_category, flag = Category.objects.get_or_create(name=category)
            self.stdout.write(f"Created category {new_category}")
        self.stdout.write(self.style.SUCCESS("Categories created"))
