from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

#in order to create a view we need a function index that takes an argument request
def index(request):
    return HttpResponse("Hello, World!")
