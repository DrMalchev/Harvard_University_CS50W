from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator


class User(AbstractUser):
    pass

class Listings(models.Model):

    categories = (
        (1, 'Fashion'),
        (2, 'Toys'),
        (3, 'Electronics'),
        (4, 'Home'),
        (5, 'Other')
    )

    title = models.CharField(max_length=64)
    description = models.CharField(max_length=124)
    starting_bid = models.FloatField(validators=[MinValueValidator(0.01)])
    image_url = models.URLField(max_length=124)
    category = models.IntegerField(choices=categories)

    comment = models.CharField(max_length=124)
    new_bid = models.FloatField(validators=[MinValueValidator(0.01)])

    def __str__(self):
        return f"{self.title} ::: {self.category} ::: {self.description} ::: {self.starting_bid}"

class Bids(models.Model):
    pass

class Comments(models.Model):
    pass