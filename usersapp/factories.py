import random

import factory
from django.conf import settings
from faker import Faker

fake = Faker(locale='ru_RU')


class CustomUserFactory(factory.DjangoModelFactory):
    class Meta:
        model = settings.AUTH_USER_MODEL

    first_name = factory.lazy_attribute(lambda x: fake.first_name())
    last_name = factory.lazy_attribute(lambda x: fake.last_name())
    username = factory.lazy_attribute(lambda x: fake.user_name())
    email = factory.lazy_attribute(lambda x: fake.safe_email())
    inn = factory.lazy_attribute(lambda x: f'{random.randint(1, 999999999999):012d}')
    balance = factory.lazy_attribute(lambda x: random.randint(0, 10000))
