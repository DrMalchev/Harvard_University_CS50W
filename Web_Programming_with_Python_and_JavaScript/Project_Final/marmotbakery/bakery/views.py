from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import datetime

from bakery.forms import PlaceOrderForm

from .models import User, Orders


def index(request):
    return render(request, "bakery/index.html", {
        
        })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "bakery/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "bakery/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "bakery/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "bakery/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "bakery/register.html")

@login_required
def placeorder(request):
    if request.method == 'POST':
        
        form = PlaceOrderForm(request.POST)
            
        if form.is_valid():

            order = Orders.objects.create(
            firstName = form.cleaned_data['firstName'],
            lastName = form.cleaned_data['lastName'],
            city = form.cleaned_data['city'],
            postCode = form.cleaned_data['postCode'],
            addressL1 = form.cleaned_data['addressL1'],
            addressL2 = form.cleaned_data['addressL2'],
            comment = form.cleaned_data['comment'],
            breadType = form.cleaned_data['breadType'],
            tel = form.cleaned_data['tel'],
            quantity = form.cleaned_data['quantity'],
            owner = request.user,
            price = form.cleaned_data['price']
            
            )

            order.save()
                
            return HttpResponseRedirect(reverse("index"))
        else:
            lastOrder = Orders.objects.filter(owner=request.user).order_by('-id')[0]
            form = PlaceOrderForm(initial=
        {'firstName': lastOrder.firstName, 
        'lastName': lastOrder.lastName,
        'city': lastOrder.city,
        'postCode': lastOrder.postCode,
        'addressL1': lastOrder.addressL1,
        'addressL2': lastOrder.addressL2,
        'tel': lastOrder.tel
        })

        return render(request, 'bakery/placeorder.html', {'form': form})

    
    else:
        checkUser = Orders.objects.filter(owner=request.user).count()
        if checkUser==0:
            form = PlaceOrderForm()
        else:
            lastOrder = Orders.objects.filter(owner=request.user).order_by('-id')[0]
            form = PlaceOrderForm(initial=
        {'firstName': lastOrder.firstName, 
        'lastName': lastOrder.lastName,
        'city': lastOrder.city,
        'postCode': lastOrder.postCode,
        'addressL1': lastOrder.addressL1,
        'addressL2': lastOrder.addressL2,
        'tel': lastOrder.tel
        })

        return render(request, 'bakery/placeorder.html', {'form': form})

def waitlist(request):
    return render(request, "bakery/waitlist.html", {
        "orders": Orders.objects.all(),
        "user": request.user,
        "date": datetime.datetime.now
        })

def myorders(request):
    return render(request, "bakery/myorders.html", {
        "orders": Orders.objects.all(),
        "user": request.user,
        "date": datetime.datetime.now
        })
