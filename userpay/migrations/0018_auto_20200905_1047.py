# Generated by Django 3.0.8 on 2020-09-05 10:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('userpay', '0017_auto_20200826_2103'),
    ]

    operations = [
        migrations.DeleteModel(
            name='WebSlider',
        ),
        migrations.AddField(
            model_name='transactiondetail',
            name='cash_payment',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='profile',
            name='current_plan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='userpay.PlanDetail'),
        ),
    ]
