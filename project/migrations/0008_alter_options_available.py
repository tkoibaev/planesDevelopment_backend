# Generated by Django 4.2.4 on 2023-10-22 23:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0007_options_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='options',
            name='available',
            field=models.BooleanField(blank=True, default=True, null=True),
        ),
    ]
