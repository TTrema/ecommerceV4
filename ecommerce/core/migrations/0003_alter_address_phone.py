# Generated by Django 4.1.7 on 2023-03-07 05:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_address_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='phone',
            field=models.IntegerField(),
        ),
    ]
