# Generated by Django 4.1.7 on 2023-03-15 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('handmade_watercolors', '0003_customer_phone_order_status_product_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='phone',
            field=models.CharField(default='', max_length=15),
        ),
    ]