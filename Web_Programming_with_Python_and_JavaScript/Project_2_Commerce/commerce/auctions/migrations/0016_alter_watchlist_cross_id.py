# Generated by Django 3.2.6 on 2021-09-16 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0015_alter_watchlist_cross_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watchlist',
            name='cross_id',
            field=models.IntegerField(),
        ),
    ]