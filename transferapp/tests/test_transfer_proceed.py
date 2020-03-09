import pytest
from django.test import TestCase, Client
from django.urls import reverse

from usersapp import factories


@pytest.mark.django_db
class TransferProceedTest(TestCase):
    """ Test module for transfer proceed """
    client = Client()

    def setUp(self):
        self.src_user_inn = '111111111111'
        self.src_user_balance = 1000
        self.src_user = factories.CustomUserFactory.create(inn=self.src_user_inn,
                                                           balance=self.src_user_balance)
        self.dst_inn = '222222222222'
        self.dst_user_balance = 1000

    def test_transfer_to_one(self):
        num_dst_users = 1
        dst_users = [factories.CustomUserFactory.create(inn=self.dst_inn, balance=self.dst_user_balance)
                     for _ in range(num_dst_users)]

        amount = self.src_user_balance * 0.5
        response = self.client.post(
            reverse('transfer_page'),
            {
                'src_user': self.src_user.pk,
                'dst_inn': self.dst_inn,
                'amount': amount,
            })

        self.assertRedirects(response,
                             reverse('transfer_success_page',
                                     kwargs={
                                         'src_user': self.src_user.pk
                                     }),
                             status_code=302,
                             target_status_code=200,
                             )

        self.src_user.refresh_from_db()
        self.assertEqual(self.src_user.balance, self.src_user_balance - amount, 'wrong src_user balance')
        for dst_user in dst_users:
            dst_user.refresh_from_db()
            self.assertEqual(dst_user.balance, self.dst_user_balance + amount / num_dst_users, 'wrong dst_user balance')

    def test_transfer_to_four(self):
        num_dst_users = 4
        dst_users = [factories.CustomUserFactory.create(inn=self.dst_inn,
                                                        balance=self.dst_user_balance)
                     for _ in range(num_dst_users)]

        amount = self.src_user_balance * 0.125
        response = self.client.post(
            reverse('transfer_page'),
            {
                'src_user': self.src_user.pk,
                'dst_inn': self.dst_inn,
                'amount': amount,
            })

        self.assertRedirects(response,
                             reverse('transfer_success_page',
                                     kwargs={
                                         'src_user': self.src_user.pk
                                     }),
                             status_code=302,
                             target_status_code=200,
                             )

        self.src_user.refresh_from_db()
        self.assertEqual(self.src_user.balance, self.src_user_balance - amount,
                         'wrong src_user balance')
        for dst_user in dst_users:
            dst_user.refresh_from_db()
            self.assertEqual(dst_user.balance, self.dst_user_balance + amount / num_dst_users,
                             'wrong dst_user balance')

    def test_transfer_balance(self):
        # case not exact rounding
        num_dst_users = 3
        dst_users = [factories.CustomUserFactory.create(inn=self.dst_inn, balance=self.dst_user_balance)
                     for _ in range(num_dst_users)]

        amount = self.src_user_balance * 0.125
        response = self.client.post(
            reverse('transfer_page'),
            {
                'src_user': self.src_user.pk,
                'dst_inn': self.dst_inn,
                'amount': amount,
            })

        self.assertRedirects(response,
                             reverse('transfer_success_page',
                                     kwargs={
                                         'src_user': self.src_user.pk
                                     }),
                             status_code=302,
                             target_status_code=200,
                             )

        self.src_user.refresh_from_db()
        src_user_delta = self.src_user.balance - self.src_user_balance
        dst_users_delta = 0
        for dst_user in dst_users:
            dst_user.refresh_from_db()
            dst_users_delta += dst_user.balance - self.dst_user_balance

        self.assertEqual(src_user_delta, -dst_users_delta, 'wrong total balance')

    def test_transfer_inn_collision(self):
        num_dst_users = 4
        dst_users = [factories.CustomUserFactory.create(inn=self.src_user_inn,
                                                        balance=self.dst_user_balance)
                     for _ in range(num_dst_users)]

        amount = self.src_user_balance * 0.125
        response = self.client.post(
            reverse('transfer_page'),
            {
                'src_user': self.src_user.pk,
                'dst_inn': self.src_user_inn,
                'amount': amount,
            })

        self.assertRedirects(response,
                             reverse('transfer_success_page',
                                     kwargs={
                                         'src_user': self.src_user.pk
                                     }),
                             status_code=302,
                             target_status_code=200,
                             )

        self.src_user.refresh_from_db()
        self.assertEqual(self.src_user.balance, self.src_user_balance - amount,
                         'wrong src_user balance')

        for dst_user in dst_users:
            dst_user.refresh_from_db()
            self.assertEqual(dst_user.balance, self.dst_user_balance + amount / num_dst_users,
                             'wrong dst_user balance')
