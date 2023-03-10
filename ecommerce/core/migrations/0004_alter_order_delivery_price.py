# Generated by Django 4.1.7 on 2023-03-09 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_order_delivery_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]