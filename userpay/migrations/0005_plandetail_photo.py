# Generated by Django 3.0.8 on 2020-07-28 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userpay', '0004_plandetail_slider'),
    ]

    operations = [
        migrations.AddField(
            model_name='plandetail',
            name='photo',
            field=models.FileField(blank=True, null=True, upload_to='plan/'),
        ),
    ]