# Generated by Django 3.2.6 on 2021-09-18 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0028_auto_20210918_1136'),
    ]

    operations = [
        migrations.AddField(
            model_name='bids',
            name='winner_id',
            field=models.IntegerField(default=0),
        ),
    ]
