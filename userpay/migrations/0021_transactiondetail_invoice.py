# Generated by Django 3.0.8 on 2020-09-06 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userpay', '0020_entertainment'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactiondetail',
            name='invoice',
            field=models.URLField(blank=True, null=True, unique=True),
        ),
    ]