from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
import datetime

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
    active = models.BooleanField(default=True)
    comment = models.CharField(max_length=124)
    new_bid = models.FloatField(validators=[MinValueValidator(0.01)])
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    

    def __str__(self):
        return f"Owner: {self.owner}/ Item: {self.title}/ Cat: {self.category}/ Price: {self.starting_bid}"

class Bids(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    desired_bid = models.FloatField(validators=[MinValueValidator(0.01)], default=None)
    winner_id= models.IntegerField(default=0)
    won_item_id = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.owner}   :::    {self.desired_bid}"

class Comments(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    comment = models.CharField( max_length=256, default=None)
    time = models.DateField(blank=True, null=True,default=datetime.date.today)
    comment_for_id = models.IntegerField(default=None)

    def __str__(self):
        return f"Comment by: {self.owner}/ Comment: {self.comment}/ Date: {self.time}/ Listing ID:{self.comment_for_id}"

class Watchlist(models.Model):
    
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    saved_item = models.CharField(max_length=128, default=None)
    cross_id = models.IntegerField()
    image_url = models.URLField(max_length=124, default=None)
    price = models.FloatField(default=None)

    def __str__(self):
        return f"Owner: {self.owner}, Item: {self.saved_item}, Item ID: {self.cross_id}, Price:{self.price} "