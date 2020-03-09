import random

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIRequestFactory, APITestCase

from api.views import CustomUserViewSet
from usersapp import factories


class CustomUserViewSetTest(APITestCase):
    """ Test module for api """
    users_qty = 40
    factory = APIRequestFactory()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        inn_src = [f'{random.randint(1, 999999999999):012d}' for _ in range(cls.users_qty // 2)]

        cls.users = [
            factories.CustomUserFactory.create(
                inn=random.choice(inn_src),
            ) for _ in range(cls.users_qty)
        ]
        cls.inn_src = list(set([el.inn for el in cls.users]))

    def test_user_get(self):
        view = CustomUserViewSet.as_view(actions={'get': 'retrieve'})

        for user in self.users:
            request = self.factory.get(reverse(
                'api:users-detail',
                kwargs={'pk': user.pk}
            ))

            response = view(request, pk=user.pk)
            assert response.status_code == 200, 'wrong status code'
            assert len(response.data) == 2, 'wrong response data length'
            assert 'inn' in response.data.keys(), 'no "inn" key'
            assert response.data.get('inn') == user.inn, 'wrong inn value'
            assert 'balance' in response.data.keys(), 'no "balance" key'
            assert float(response.data.get('balance')) == user.balance, 'wrong balance value'

    def test_inn_filter(self):
        view = CustomUserViewSet.as_view(actions={'get': 'list'})

        for user in self.users:
            request = self.factory.get(f'{reverse("api:users-list")}?inn={user.inn}')
            response = view(request)
            db_data = get_user_model().objects.filter(inn=user.inn)
            response_inn = {el.get('inn') for el in response.data}
            assert response.status_code == 200, 'wrong status code'
            assert len(response_inn) == 1, 'wrong response inn'
            assert len(response.data) == db_data.count(), 'wrong response data length'
