from django.db import models

# Create your models here.


# one model for each of the created tables for information storage
# each model will be a separate class
#
class Flight(models.Model):
    origin = models.CharField(max_length=64)
    destination = models.CharField(max_length=64)
    duration = models.IntegerField()
    