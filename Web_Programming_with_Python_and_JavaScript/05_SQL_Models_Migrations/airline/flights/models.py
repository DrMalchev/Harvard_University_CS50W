from django.db import models
from django.db.models.fields.related import ManyToManyField

# Create your models here.


# one model for each of the created tables for information storage
# each model will be a separate class
#

# After change in models.py ->
# py manage.py makemigrations 
# py manage.py migrate
# back into the shell -> py manage.py shell
# !! pay attention command is executed in the folder where manage.py !!

class Airport(models.Model):
    code = models.CharField(max_length=3)
    # airport code for example MUC for Munich
    city = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.city} ({self.code})"

class Flight(models.Model):
    origin = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="departures")
    # if I delete an airport, models.CASCADE will also delete any corresponding flights
    # that are part of other table
    # related name gives info in oposite direction
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="arrivals")
    duration = models.IntegerField()
    
    # in every class we can define a funcion __str__ that implemets a string representation of the object
    # instead of calling it Object 1 etc.

    def __str__(self) -> str:
        return f"{self.id}: {self.origin} to {self.destination}"

class Passenger(models.Model):
    
    first = models.CharField(max_length=64)
    last = models.CharField(max_length=64)
    flights = models.ManyToManyField(Flight, blank=True, related_name="passengers")
    # related name gives access of Flight to Passengers

    def __str__(self):
        return f"{self.first} {self.last}"