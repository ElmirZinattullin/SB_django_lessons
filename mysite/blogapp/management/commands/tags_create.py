from django.core.management import BaseCommand
from django.db import transaction

from blogapp.models import Tag


class Command(BaseCommand):
    @transaction.atomic()
    def handle(self, *args, **options):
        self.stdout.write("Create tags")

        tags = [
            'russia',
            'poem',
            '18th century',
            '19th century',
            'world',
            'peace',
            'qwer123',
            'new_tag',
            'true_story'
            'new',
            'old',
        ]
        for tag in tags:
            new_tag, flag = Tag.objects.get_or_create(name=tag)
            self.stdout.write(f"Created tag {new_tag}")
        self.stdout.write(self.style.SUCCESS("Tags created"))
