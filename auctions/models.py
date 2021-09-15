from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE
from djmoney.models.fields import MoneyField
from djmoney.models.validators import MinMoneyValidator
from ckeditor.fields import RichTextField


class User(AbstractUser):
    pass


class Lot(models.Model):
    seller = models.ForeignKey(
        User, on_delete=CASCADE, related_name="lots")
    title = models.CharField(max_length=64)
    description = RichTextField()
    bid = MoneyField(max_digits=10, decimal_places=2,
                     default_currency='USD', validators=[
                         MinMoneyValidator(Decimal('0.01')),
                     ])
    image = models.ImageField(upload_to='lot_images/', null=True, blank=True)
    category = models.CharField(max_length=32, null=True, blank=True)
    add_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

