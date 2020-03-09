from math import floor

import django.forms as forms
from django.core.validators import RegexValidator
from django.db import transaction
from django.db.models import F
from django.utils.translation import gettext_lazy as _

from usersapp.models import CustomUser


class TranferForm(forms.Form):
    src_user = forms.ModelChoiceField(
        label='отправитель',
        queryset=CustomUser.objects.filter(balance__gt=0)
    )

    dst_inn = forms.CharField(
        label='ИНН получателя',
        min_length=12,
        max_length=12,
        required=True,
        validators=[RegexValidator(r'\d{12}')]
    )
    amount = forms.DecimalField(label='сумма', max_digits=12, decimal_places=2, required=True)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if not amount:
            raise forms.ValidationError(_('not set amount of money to transfer'))

        src_user = self.cleaned_data.get('src_user')
        if src_user and amount and src_user.balance < amount:
            raise forms.ValidationError(
                _('src_user have not enough money'),
                code='invalid',
                params={'balance': src_user.balance, 'amount': amount}
            )

        return amount

    def is_valid(self):
        super().is_valid()
        src_user = self.cleaned_data.get('src_user')
        dst_inn = self.cleaned_data.get('dst_inn')
        if src_user and dst_inn:
            dst_users = CustomUser.objects.exclude(pk=src_user.pk).filter(inn=dst_inn)
            if not dst_users.exists():
                self.add_error(
                    'dst_inn',
                    forms.ValidationError(
                        _('no users with this inn found'),
                        code='invalid',
                        params={'dst_inn': dst_inn}
                    )
                )

        return super().is_valid()

    def save(self):
        src_user = self.cleaned_data.get('src_user')
        dst_inn = self.cleaned_data.get('dst_inn')
        amount = self.cleaned_data.get('amount')
        dst_users = CustomUser.objects.exclude(pk=self.cleaned_data.get('src_user').pk).filter(inn=dst_inn)
        dst_users_count = dst_users.count()
        with transaction.atomic():
            # round dst_users parts to lower
            dst_users_amount = floor(amount / dst_users_count * 100) / 100
            dst_users.update(balance=F('balance') + dst_users_amount)
            # do src_user payment correction because of divided in parts
            src_user_payment = dst_users_amount * dst_users_count
            src_user.balance = F('balance') - src_user_payment
            src_user.save()

        return src_user
