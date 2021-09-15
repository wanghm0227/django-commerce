# Generated by Django 3.2.5 on 2021-09-13 12:50

from decimal import Decimal
from django.db import migrations, models
import django.utils.timezone
import djmoney.models.fields
import djmoney.models.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_alter_lot_seller'),
    ]

    operations = [
        migrations.AddField(
            model_name='lot',
            name='add_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='lot',
            name='bid',
            field=djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0'), default_currency='USD', max_digits=10, validators=[djmoney.models.validators.MinMoneyValidator(Decimal('0.01'))]),
        ),
    ]
