from random import choice

from django.core.management import BaseCommand
from django.db import transaction

from blogapp.models import Article, Tag, Category, Author


class Command(BaseCommand):
    @transaction.atomic()
    def handle(self, *args, **options):
        self.stdout.write("Create articles")

        Pushkin = {'Талисман': f"Там, где море вечно плещет"
                               f"\nНа пустынные скалы,"
                               f"\nГде луна теплее блещет"
                               f"\nВ сладкий час вечерней мглы,"
                               f"\nГде, в гаремах наслаждаясь,"
                               f"\nДни проводит мусульман,"
                               f"\nТам волшебница, ласкаясь,"
                               f"\nМне вручила талисман.",
                   'Цветок': "\nЦветок засохший, безуханный,"
                             "\nЗабытый в книге вижу я;"
                             "\nИ вот уже мечтою странной"
                             "\nДуша наполнилась моя:",
                   }
        Lermontov = {
            "Утес": ""
                    "Ночевала тучка золотая"
                    "\nНа груди утеса-великана;"
                    "\nУтром в путь она умчалась рано,"
                    "\nПо лазури весело играя;",
            "Сон": ""
                   "\nИ снился мне сияющий огнями"
                   "\nВечерний пир, в родимой стороне."
                   "\nМеж юных жен, увенчанных цветами,"
                   "\nШел разговор веселый обо мне.",
        }
        Esenin = {
            "Товарищ": ""
                       "\nОн был сыном простого рабочего,"
                       "\nИ повесть о нем очень короткая."
                       "\nТолько и было в нем, что волосы, как ночь,"
                       "\nДа глаза голубые, кроткие.",
            "Пороша": ""
                      "\nЕду. Тихо. Слышны звоны"
                      "\nПод копытом на снегу."
                      "\nТолько серые вороны"
                      "\nРасшумелись на лугу."
        }
        poems = {"Pushkin": Pushkin, "Lermontov": Lermontov, "Esenin": Esenin}

        tags = list(Tag.objects.all())
        category_list = list(Category.objects.all())
        print(tags)
        print(category_list)

        for author, poems_dict in poems.items():
            article_author = list(Author.objects.filter(name=author))[0]
            for title, content in poems_dict.items():
                new_article, status = Article.objects.get_or_create(author=article_author,
                                      title=title,
                                      content=content,
                                      category=choice(category_list))
                self.stdout.write(f"Created poem {new_article}")
                for _ in range(2):
                    new_article.tags.add(choice(tags))
                self.stdout.write(f"tags add")
                new_article.save
        self.stdout.write(self.style.SUCCESS("All articles created"))

#
# class Article(models.Model):
#     title = models.CharField(max_length=200)
#     content = models.TextField(null=False, blank=True)
#     pub_date = models.DateTimeField(auto_now_add=True, null=False, blank=True)
#     author = models.ForeignKey(Author, on_delete=models.CASCADE)
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     tags = models.ManyToManyField(Tag, related_name="articles")
