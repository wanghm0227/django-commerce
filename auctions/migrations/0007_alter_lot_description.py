# Generated by Django 3.2.5 on 2021-09-14 08:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_alter_lot_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lot',
            name='description',
            field=models.TextField(),
        ),
    ]
