from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.fields.reverse_related import OneToOneRel
from djmoney.models.fields import MoneyField
from djmoney.models.validators import MinMoneyValidator


class User(AbstractUser):
    pass


class Lot(models.Model):
    seller = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="auction_lots")
    buyer = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="purchased_lot", null=True)
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=64)
    description = models.TextField()
    bid = MoneyField(max_digits=10, decimal_places=2,
                     default_currency='USD', validators=[
                         MinMoneyValidator(Decimal('0.01')),
                     ])
    image = models.ImageField(upload_to='lot_images/', null=True, blank=True)
    category = models.CharField(max_length=32, null=True, blank=True)
    add_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return '/listings/%i/' % self.id


class Bid(models.Model):
    price = MoneyField(max_digits=10, decimal_places=2,
                       default_currency='USD', validators=[
                           MinMoneyValidator(Decimal('0.01')),
                       ])
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f'{self.price} - {self.lot} - {self.bidder}'


class Watchlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    lots = models.ManyToManyField(Lot, blank=True)

    def __str__(self):
        return str(self.user)


class Comment(models.Model):
    lot = models.ForeignKey(
        Lot, on_delete=models.CASCADE, related_name="comments")
    commenter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField(max_length=255)
    add_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.lot) + ' - ' + str(self.commenter)
