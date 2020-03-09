import random

from django.core.management import BaseCommand

from usersapp import factories


class Command(BaseCommand):
    help = 'Generate users'

    def handle(self, *args, **options):
        users_qty = 30
        inn_src = [f'{random.randint(1, 999999999999):012d}' for _ in range(users_qty // 2)]
        [factories.CustomUserFactory.create(inn=random.choice(inn_src)) for _ in range(users_qty)]
