# Generated by Django 3.0.8 on 2020-08-26 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userpay', '0015_plandetailweb'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entertainment',
            name='title',
            field=models.CharField(max_length=50, verbose_name='Link'),
        ),
        migrations.AlterField(
            model_name='webslider',
            name='title',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
