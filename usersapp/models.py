from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    inn = models.CharField(max_length=12, db_index=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0, db_index=True)

    def __str__(self):
        return f'{self.username} ({self.last_name} {self.first_name})'

    class Meta:
        ordering = ['username']
