from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings

class User(AbstractUser):
    pass

class Listings(models.Model):

    categories = (
        ('Fashion', 'Fashion'),
        ('Toys', 'Toys'),
        ('Electronics', 'Electronics'),
        ('Home', 'Home'),
        ('Other', 'Other')
    )

    title = models.CharField(max_length=64)
    description = models.CharField(max_length=124)
    starting_bid = models.FloatField(validators=[MinValueValidator(0.01)])
    image_url = models.URLField(max_length=124)
    category = models.CharField(max_length=64, choices=categories)

    comment = models.CharField(max_length=124)
    new_bid = models.FloatField(validators=[MinValueValidator(0.01)])
    

    def __str__(self):
        return f"{self.title}   :::   {self.category}   :::    {self.starting_bid}"

class Bids(models.Model):
    pass

class Comments(models.Model):
    pass

class Watchlist(models.Model):
    
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    saved_item = models.CharField(max_length=128, default=None)
    cross_id = models.IntegerField()
    image_url = models.URLField(max_length=124, default=None)
    price = models.FloatField(default=None)

    def __str__(self):
        return f"Owner: {self.owner}, Item: {self.saved_item}, Item ID: {self.cross_id}, Price:{self.price} "