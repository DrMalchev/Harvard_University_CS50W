
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models.aggregates import Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from datetime import date, datetime, timedelta, time
from django.db.models import Count
from django import template
import collections
register = template.Library()

from bakery.forms import EditForm, PlaceOrderForm

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
            if Orders.objects.all().count()==0:
                cumuTemp=0
                lastDeliveryDate = datetime.now().date() + timedelta(days = 2)
            else:
                cumuTemp=Orders.objects.filter(processed = 0).aggregate(Sum('quantity'))['quantity__sum']
                lastDeliveryDate = Orders.objects.order_by('-deliveryTime').latest('deliveryTime').deliveryTime.date()

            check = 10 #max daily capacity
            deliveryOn = lastDeliveryDate
            #check if daily orders exceed capacity of 10 and reshedule for day + 1
            if cumuTemp >= check:
                cumuTemp = 0
                
                Orders.objects.all().update(processed =1)
                deliveryOn = lastDeliveryDate + timedelta(days = 1)
                
            #check if order is received after 21:00 CET and  reshedule for day + 1
            #Sourdough has to be prepared for the next day. if order comes in after 21:00 CET
            #there will be no soudough for its completion => reshedule
            #
            #special case: additional check if delivery date is more than 2 days from now
            #if yes, order is not resheduled, because the sourdough planning can be made
            #2 days in advance
            #
            lastDeliveryDate2 = Orders.objects.order_by("-id").values("deliveryTime").first()["deliveryTime"].date() 
            if datetime.now().hour > 21  and lastDeliveryDate2 > datetime.now().date() + timedelta(days = 2): 
                if Orders.objects.order_by('-deliveryTime').latest('processed').processed == 1:
                    deliveryOn = lastDeliveryDate
                else:
                    deliveryOn = lastDeliveryDate + timedelta(days = 1)
                    Orders.objects.all().update(processed =1)
                    cumuTemp = 0
            
            #special case when user orders more than 1 bread and exceeds the capacity of 10
            #therefore the cumulative value and the delivery date have to be corrected
            #because the model accepts cumulative value greater than 10
            if cumuTemp + form.cleaned_data['quantity'] > check:
                cumuTemp = 0
                deliveryOn = Orders.objects.order_by('-deliveryTime').latest('deliveryTime').deliveryTime.date() + timedelta(days = 1)
                Orders.objects.all().update(processed =1)

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
            price = form.cleaned_data['price'],
            orderTime = datetime.now().replace(microsecond=0),
            brake = False,
            deliveryTime = deliveryOn,
            cumulative = cumuTemp + form.cleaned_data['quantity']
            
            )
            order.save()
           
            return HttpResponseRedirect(reverse("waitlist"))
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

    
    else: #request is GET, render empty form
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

        if Orders.objects.all().count() ==0:
            maxDailyLeft = 10
        else:
            maxDailyLeft = Orders.objects.all().last().cumulative
            if maxDailyLeft==10:
                maxDailyLeft=10
            else:
                maxDailyLeft = 10 - Orders.objects.all().last().cumulative
        return render(request, 'bakery/placeorder.html', {
            'form': form,
            'maxDailyLeft': maxDailyLeft
            })

def waitlist(request):
    totalCount = Orders.objects.aggregate(Sum('quantity'))['quantity__sum']
    lastDeliveryDate = Orders.objects.order_by("-id").values("deliveryTime").first()["deliveryTime"].date() 
    #test case if a bread should be acepted
    #placed in this section just to check results in the template
    #ifAccepted = False
    #if lastDeliveryDate > datetime.now().date() + timedelta(days = 2):
    #    ifAccepted = True        
    return render(request, "bakery/waitlist.html", {
        "orders": Orders.objects.filter(orderTime__gt = datetime.today().date()).order_by('deliveryTime').all(),
        "ordersAll": Orders.objects.order_by('deliveryTime').all(),
        "user": request.user,
        "totalCount": totalCount,
        "timePlus2Days": datetime.now().date() + timedelta(days = 2),
        #"lastDeliveryDate": lastDeliveryDate,
        #"ifAccepted": ifAccepted
        # Bread needs 2 days after ordering to be ready
        })

def myorders(request):
    
    summaryByType = {}
    
    for order in  Orders.objects.filter(owner = request.user):
        if order.breadType in summaryByType:
            summaryByType[order.breadType] = order.quantity + summaryByType[order.breadType]
        else:
            summaryByType[order.breadType] = order.quantity
    today = datetime.today()
    mostOrdered = max(summaryByType, key=summaryByType.get)
    #sorted(summaryByType.items(), key=lambda x: x[1], reverse=True)
    return render(request, "bakery/myorders.html", {
        "summaryByType": sorted(summaryByType.items(), key=lambda x: x[1], reverse=True),
        "orders": Orders.objects.filter(owner = request.user, deliveryTime__gte=today).all(),
        "ordersAll": Orders.objects.filter(owner = request.user).values('breadType').distinct(),
        "ordersHistory": Orders.objects.filter(owner = request.user, deliveryTime__lte=today).all(),
        "user": request.user,
        "mostOrderedCount": summaryByType[mostOrdered],
        "mostOrdered": mostOrdered
        
        })

def edit(request, id):
    if request.method == 'POST':
        form = EditForm(request.POST)
    else:
        editData = Orders.objects.get(pk=id)
        form = EditForm(initial=
        {'quantity': editData.quantity,
        'breadType':editData.breadType,
        'price': editData.price
        
        })

    return render(request, "bakery/edit.html", {
        
        "orders": Orders.objects.filter(owner = request.user).all(),
        "id": id,
        "form": form,
        "user": request.user,
        
        
        })

