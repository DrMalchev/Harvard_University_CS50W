
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.

from .models import Flight, Passenger
from django.urls import reverse

def index(request):
    return render(request, "flights/index.html", {
        "flights": Flight.objects.all()
    })

def flight(request, flight_id):
    
    flight = Flight.objects.get(id=flight_id)
    # alternatively I can use pk (primary key) which is id
    #flight = Flight.objects.get(pk=flight_id)
    return render(request, "flights/flight.html", {
        "flight": flight,
        "passengers": flight.passengers.all(), 
        "non_passengers": Passenger.objects.exclude(flights=flight).all()
        # passengers is the related name in models.py

    })

def book(request, flight_id):
    passenger_id = int(request.POST["passenger"])
    if request.method == "POST":
        flight = Flight.objects.get(pk=flight_id)
        passenger = Passenger.objects.get(pk=passenger_id) 
        # info will be parsed by a form with input field named passenger
        passenger.flights.add(flight)
        return HttpResponseRedirect(reverse("flight", args=(flight_id,)))
        # reverse takes the name of particular view and finds the url from url paths