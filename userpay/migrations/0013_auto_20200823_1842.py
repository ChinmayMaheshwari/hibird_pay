# Generated by Django 3.0.8 on 2020-08-23 18:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userpay', '0012_auto_20200823_1832'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='userid',
            new_name='user',
        ),
    ]
