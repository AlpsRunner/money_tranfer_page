import random

import pytest
from django.core.validators import RegexValidator
from django.forms import Field, ModelChoiceField
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from transferapp.forms import TranferForm
from usersapp import factories


@pytest.mark.django_db
class TransferPageTest(TestCase):
    """ Test module for transfer page """
    users_qty = 20
    client = Client()

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

    def setUp(self):
        self.valid_src_user = random.choice(self.users)
        _inn_src = self.inn_src.copy()
        _inn_src.remove(self.valid_src_user.inn)
        self.valid_inn_src = _inn_src

    def test_transfer_form_render(self):
        response = self.client.get(reverse('transfer_page'))
        assert response.status_code == 200, 'wrong status_code'

        form = response.context.get('form')
        assert 'src_user' in form.fields, 'no "src_user" field in form'
        assert 'dst_inn' in form.fields, 'no "dst_inn" field in form'
        assert 'amount' in form.fields, 'no "amount" field in form'

        assert len(form.fields.get('src_user').queryset) == \
               len(list(filter(lambda x: x.balance > 0, self.users))), \
            'wrong users count in "src_user" field'

    def test_transfer_form_valid_data(self):
        form = TranferForm({
            'src_user': self.valid_src_user.pk,
            'dst_inn': random.choice(self.valid_inn_src),
            'amount': random.randint(1, self.valid_src_user.balance),
        })

        assert form.is_valid(), 'form is not valid'

    def test_transfer_form_empty_src_user(self):
        form = TranferForm({
            'dst_inn': random.choice(self.valid_inn_src),
            'amount': random.randint(1, self.valid_src_user.balance),
        })

        assert not form.is_valid(), 'form is valid'
        assert 'src_user' in form.errors.keys(), 'no key in form errors'
        assert form.errors.get('src_user') == [Field.default_error_messages['required']], \
            'wrong error message'

    def test_transfer_form_wrong_src_user(self):
        form = TranferForm({
            'src_user': 0,
            'dst_inn': random.choice(self.valid_inn_src),
            'amount': random.randint(1, self.valid_src_user.balance),
        })

        assert not form.is_valid(), 'form is valid'
        assert 'src_user' in form.errors.keys(), 'no key in form errors'
        assert form.errors.get('src_user') == \
               [ModelChoiceField.default_error_messages['invalid_choice']], \
            'wrong error message'

    def test_transfer_form_empty_dst_inn(self):
        form = TranferForm({
            'src_user': self.valid_src_user.pk,
            'amount': random.randint(1, self.valid_src_user.balance),
        })

        assert not form.is_valid(), 'form is valid'
        assert 'dst_inn' in form.errors.keys(), 'no key in form errors'
        assert form.errors.get('dst_inn') == [Field.default_error_messages['required']], \
            'wrong error message'

    def test_transfer_form_wrong_dst_inn(self):
        # short inn case
        form = TranferForm({
            'src_user': self.valid_src_user.pk,
            'dst_inn': '1111',
            'amount': random.randint(1, self.valid_src_user.balance),
        })

        assert not form.is_valid(), 'form is valid'
        assert 'dst_inn' in form.errors.keys(), 'no key in form errors'
        assert RegexValidator.message in form.errors.get('dst_inn'), \
            'wrong error message for short case'

        # inn with letters case
        form = TranferForm({
            'src_user': self.valid_src_user.pk,
            'dst_inn': '1111hello999',
            'amount': random.randint(1, self.valid_src_user.balance),
        })

        assert not form.is_valid(), 'form is valid'
        assert 'dst_inn' in form.errors.keys(), 'no key in form errors'
        assert RegexValidator.message in form.errors.get('dst_inn'), \
            'wrong error message for letter case'

    def test_transfer_form_not_exists_dst_inn(self):
        dst_inn = '000000000000'
        form = TranferForm({
            'src_user': self.valid_src_user.pk,
            'dst_inn': dst_inn,
            'amount': random.randint(1, self.valid_src_user.balance),
        })

        assert not form.is_valid(), 'form is valid'
        assert 'dst_inn' in form.errors.keys(), 'no key in form errors'
        assert form.errors.get('dst_inn') == [_('no users with this inn found')], \
            'wrong error message'

    def test_transfer_form_empty_amount(self):
        form = TranferForm({
            'src_user': self.valid_src_user.pk,
            'dst_inn': random.choice(self.valid_inn_src),
        })

        assert not form.is_valid(), 'form is valid'
        assert 'amount' in form.errors.keys(), 'no key in form errors'
        assert form.errors.get('amount') == [Field.default_error_messages['required']], \
            'wrong error message'

    def test_transfer_form_wrong_amount(self):
        # zero amount case
        form = TranferForm({
            'src_user': self.valid_src_user.pk,
            'dst_inn': random.choice(self.valid_inn_src),
            'amount': 0,
        })

        assert not form.is_valid(), 'form is valid'
        assert 'amount' in form.errors.keys(), 'no key in form errors'
        assert form.errors.get('amount') == [_('not set amount of money to transfer')], \
            'wrong error message for zero amount case'

        # not enough balance case
        form = TranferForm({
            'src_user': self.valid_src_user.pk,
            'dst_inn': random.choice(self.valid_inn_src),
            'amount': self.valid_src_user.balance + 100,
        })

        assert not form.is_valid(), 'form is valid'
        assert 'amount' in form.errors.keys(), 'no key in form errors'
        assert form.errors.get('amount') == [_('src_user have not enough money')], \
            'wrong error message for not enough balance case'
