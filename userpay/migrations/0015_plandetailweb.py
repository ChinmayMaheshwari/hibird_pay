# Generated by Django 3.0.8 on 2020-08-26 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userpay', '0014_auto_20200824_2048'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlanDetailWeb',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month_detail', models.CharField(default='Monthly', max_length=20)),
                ('amount', models.PositiveIntegerField()),
                ('speed_detail', models.PositiveIntegerField()),
                ('data_per_month', models.CharField(default='Unlimited', max_length=10)),
                ('offer_detail', models.CharField(default='NA', max_length=50)),
            ],
        ),
    ]
