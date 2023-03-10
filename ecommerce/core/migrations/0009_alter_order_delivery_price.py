# Generated by Django 4.1.7 on 2023-03-10 03:21

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_order_ref_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
