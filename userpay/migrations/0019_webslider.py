# Generated by Django 3.0.8 on 2020-09-05 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userpay', '0018_auto_20200905_1047'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebSlider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=50, null=True)),
                ('photo', models.FileField(upload_to='slider/')),
            ],
        ),
    ]
