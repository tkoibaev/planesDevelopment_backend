# Generated by Django 4.2.4 on 2023-10-21 11:22

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0005_alter_applications_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='options',
            name='image',
        ),
        migrations.AddField(
            model_name='options',
            name='price',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10),
        ),
    ]
