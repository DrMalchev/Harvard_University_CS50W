# Generated by Django 3.2.6 on 2021-09-15 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0008_alter_listings_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='Watchlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner', models.CharField(max_length=64)),
                ('saved_item', models.ManyToManyField(blank=True, related_name='saved_item', to='auctions.Listings')),
            ],
        ),
    ]