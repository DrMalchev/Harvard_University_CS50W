from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

#in order to create a view we need a function index that takes an argument request
def index(request):
    return render(request, "hello/index.html")

def delyan(request):
    return(HttpResponse("Hello, Delyan!"))

def david(request):
    return(HttpResponse("Hello, David!"))

def greet(request, name):
    return render(request, "hello/greet.html", {
        "name": name.capitalize()
    })
