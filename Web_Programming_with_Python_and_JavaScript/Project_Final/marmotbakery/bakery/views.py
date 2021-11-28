
from .models import User, Orders
from bakery.forms import EditForm, PlaceOrderForm
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
from collections import defaultdict


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
            if Orders.objects.all().count() == 0:
                cumuTemp = 0
                lastDeliveryDate = datetime.now().date() + timedelta(days=2)
            elif Orders.objects.all().count() is not 0 and Orders.objects.order_by(
                #if user has not ordered bread for 2-3 days. but it is not empty db so app gets lastdate
                #from db and ques. but we need 2 days to deliver, so it should be corrected with +2 days
                    '-deliveryTime').latest('deliveryTime').deliveryTime.date() < datetime.now().date() + timedelta(days=2):
                lastDeliveryDate = datetime.now().date() + timedelta(days=2)
                cumuTemp = Orders.objects.filter(processed=0).aggregate(
                    Sum('quantity'))['quantity__sum']
            else:
                cumuTemp = Orders.objects.filter(processed=0).aggregate(
                    Sum('quantity'))['quantity__sum']
                lastDeliveryDate = Orders.objects.order_by(
                    '-deliveryTime').latest('deliveryTime').deliveryTime.date()

            check = 10  # max daily capacity
            deliveryOn = lastDeliveryDate
            # check if daily orders exceed capacity of 10 and reshedule for day + 1
            #
            # special case, bug fix: no orders, user makes first order, then deletes it. cumuTemp is now None
            # and has to be corrected to zero again
            if cumuTemp is None:
                cumuTemp=0
            if cumuTemp >= check:
                cumuTemp = 0

                Orders.objects.all().update(processed=1)
                deliveryOn = lastDeliveryDate + timedelta(days=1)

            # check if order is received after 21:00 CET and  reshedule for day + 1
            # Sourdough has to be prepared for the next day. if order comes in after 21:00 CET
            # there will be no soudough for its completion => reshedule
            #
            # special case: additional check if delivery date is more than 2 days from now
            # if yes, order is not resheduled, because the sourdough planning can be made
            # 2 days in advance
            #
            if Orders.objects.all().count() != 0:
                lastDeliveryDate2 = Orders.objects.order_by(
                    "-id").values("deliveryTime").first()["deliveryTime"].date()
                if datetime.now().hour > 21 and lastDeliveryDate2 > datetime.now().date() + timedelta(days=2):
                    if Orders.objects.order_by('-deliveryTime').latest('processed').processed == 1:
                        deliveryOn = lastDeliveryDate
                    else:
                        deliveryOn = lastDeliveryDate + timedelta(days=1)
                        Orders.objects.all().update(processed=1)
                        cumuTemp = 0

            # special case when user orders more than 1 bread and exceeds the capacity of 10
            # therefore the cumulative value and the delivery date have to be corrected
            # because the model accepts cumulative value greater than 10
            if cumuTemp + form.cleaned_data['quantity'] > check:
                cumuTemp = 0
                deliveryOn = Orders.objects.order_by(
                    '-deliveryTime').latest('deliveryTime').deliveryTime.date() + timedelta(days=1)
                Orders.objects.all().update(processed=1)

            order = Orders.objects.create(
                firstName=form.cleaned_data['firstName'],
                lastName=form.cleaned_data['lastName'],
                city=form.cleaned_data['city'],
                postCode=form.cleaned_data['postCode'],
                addressL1=form.cleaned_data['addressL1'],
                addressL2=form.cleaned_data['addressL2'],
                comment=form.cleaned_data['comment'],
                breadType=form.cleaned_data['breadType'],
                tel=form.cleaned_data['tel'],
                quantity=form.cleaned_data['quantity'],
                owner=request.user,
                price=form.cleaned_data['price'],
                orderTime=datetime.now().replace(microsecond=0),
                brake=False,
                deliveryTime=deliveryOn,
                cumulative=cumuTemp + form.cleaned_data['quantity']

            )
            order.save()

            return HttpResponseRedirect(reverse("waitlist"))
        else:
            lastOrder = Orders.objects.filter(
                owner=request.user).order_by('-id')[0]
            form = PlaceOrderForm(initial={'firstName': lastOrder.firstName,
                                           'lastName': lastOrder.lastName,
                                           'city': lastOrder.city,
                                           'postCode': lastOrder.postCode,
                                           'addressL1': lastOrder.addressL1,
                                           'addressL2': lastOrder.addressL2,
                                           'tel': lastOrder.tel
                                           })

        return render(request, 'bakery/placeorder.html', {'form': form})

    else:  # request is GET, render empty form
        checkUser = Orders.objects.filter(owner=request.user).count()
        if checkUser == 0:
            form = PlaceOrderForm()
        else:
            lastOrder = Orders.objects.filter(
                owner=request.user).order_by('-id')[0]
            form = PlaceOrderForm(initial={'firstName': lastOrder.firstName,
                                           'lastName': lastOrder.lastName,
                                           'city': lastOrder.city,
                                           'postCode': lastOrder.postCode,
                                           'addressL1': lastOrder.addressL1,
                                           'addressL2': lastOrder.addressL2,
                                           'tel': lastOrder.tel
                                           })

        if Orders.objects.all().count() == 0:
            maxDailyLeft = 10
        else:
            maxDailyLeft = Orders.objects.all().last().cumulative
            if maxDailyLeft == 10:
                maxDailyLeft = 10
            else:
                maxDailyLeft = 10 - Orders.objects.all().last().cumulative
        return render(request, 'bakery/placeorder.html', {
            'form': form,
            'maxDailyLeft': maxDailyLeft
        })


def waitlist(request):
    totalCount = Orders.objects.aggregate(Sum('quantity'))['quantity__sum']
    lastDeliveryDate = Orders.objects.order_by(
        "-id").values("deliveryTime").first()["deliveryTime"].date()
    # test case if a bread should be acepted
    # placed in this section just to check results in the template
    #ifAccepted = False
    # if lastDeliveryDate > datetime.now().date() + timedelta(days = 2):
    #    ifAccepted = True
    return render(request, "bakery/waitlist.html", {
        "orders": Orders.objects.filter(deliveryTime__gt=datetime.today().date()).order_by('deliveryTime').all(),
        "ordersAll": Orders.objects.order_by('deliveryTime').all(),
        "user": request.user,
        "totalCount": totalCount,
        "timePlus2Days": datetime.now().date() + timedelta(days=2),
        # "lastDeliveryDate": lastDeliveryDate,
        # "ifAccepted": ifAccepted
        # Bread needs 2 days after ordering to be ready
    })


def myorders(request):

    summaryByType = {}
    if Orders.objects.filter(owner=request.user).all().count() != 0:
        for order in Orders.objects.filter(owner=request.user):
            if order.breadType in summaryByType:
                summaryByType[order.breadType] = order.quantity + \
                    summaryByType[order.breadType]
            else:
                summaryByType[order.breadType] = order.quantity
        today = datetime.today()
        mostOrdered = max(summaryByType, key=summaryByType.get)
        #sorted(summaryByType.items(), key=lambda x: x[1], reverse=True)
        return render(request, "bakery/myorders.html", {
            "summaryByType": sorted(summaryByType.items(), key=lambda x: x[1], reverse=True),
            "orders": Orders.objects.filter(owner=request.user, deliveryTime__gte=today).all(),
            "ordersAll": Orders.objects.filter(owner=request.user).values('breadType').distinct(),
            "ordersHistory": Orders.objects.filter(owner=request.user, deliveryTime__lte=today).all(),
            "user": request.user,
            "mostOrderedCount": summaryByType[mostOrdered],
            "mostOrdered": mostOrdered

        })
    else:
        return render(request, "bakery/myorders.html", {})


def edit(request, id):
    # TODO
    # forbid editing of orders that are processed
    #
    if request.method == 'POST':
        form = EditForm(request.POST)
        if form.is_valid():
            # calculate the updated cumulative of this order
            # Note: it also affects all orders from that day
            oldQuantity = Orders.objects.get(pk=id).quantity
            oldCumulative = Orders.objects.get(pk=id).cumulative
            deltaQuantity = oldQuantity - form.cleaned_data['quantity']
            newCumulative = oldCumulative - deltaQuantity
            # update edited order
            Orders.objects.filter(pk=id).update(
                breadType=form.cleaned_data['breadType'],
                quantity=form.cleaned_data['quantity'],
                price=form.cleaned_data['price'],
                #cumulative = newCumulative
                # cumulative is updated bellow and must not be changed here
            )
            # update cumulative index of all other orders from that day
            #
            # get the date
            thisDate = Orders.objects.get(pk=id).deliveryTime.date()
            obj = Orders.objects.filter(deliveryTime=thisDate).all()
            for orderW in Orders.objects.filter(deliveryTime=thisDate).all():
                # get current cumulative
                currentOrderCumu = Orders.objects.get(pk=orderW.pk).cumulative
                updateCumu = currentOrderCumu - deltaQuantity
                Orders.objects.filter(pk=orderW.pk).update(
                    cumulative=updateCumu)

            return HttpResponseRedirect(reverse("myorders"))
            # return render(request, "bakery/myorders.html", {
            #     "thisDate": thisDate,
            #     "obj":obj
            # })

    else:  # request is GET
        form = EditForm()

        editData = Orders.objects.get(pk=id)
        form = EditForm(initial={'quantity': editData.quantity,
                                 'breadType': editData.breadType,
                                 'price': editData.price

                                 })
        thisDeliveryDate = Orders.objects.get(pk=id).deliveryTime.date()
        maxCumuForDeliveryDate = Orders.objects.filter(
            deliveryTime=thisDeliveryDate).order_by('pk').last().cumulative
        allowedAdditional = 10-maxCumuForDeliveryDate
                
        return render(request, "bakery/edit.html", {
            "allowedAdditional": allowedAdditional,
            "orders": Orders.objects.filter(owner=request.user, deliveryTime__gte=datetime.now()).all(),
            "id": id,
            "form": form,
            "user": request.user
            
           })


def delete(request, id):
    # 
    # forbid deleteion of orders that are processed
    # done in the front end with JS

    # get the quantity of the deleted order
    # Note: it also affects all orders from that day
    deletedQuantity = Orders.objects.get(pk=id).quantity
    
    # update cumulative index of all other orders from that day
    # special case:
    # ONLY orders older that the deleted are affected and should be updated
    # otherwise previous orders get wrong cumulative index
    #
    # get the date
    thisDate = Orders.objects.get(pk=id).deliveryTime.date()
    
    for orderD in Orders.objects.filter(deliveryTime=thisDate, pk__gt=id).all():
        # get current cumulative
        currentOrderCumu = Orders.objects.get(pk=orderD.pk).cumulative
        updateCumu = currentOrderCumu - deletedQuantity
        Orders.objects.filter(pk=orderD.pk).update(cumulative=updateCumu)
    #
    # add one cancelation point for this user
    # to be used in admin metrics
    for user in User.objects.filter(username__iexact=request.user.username):
        user.cancelations+=1
        user.save()
    Orders.objects.filter(pk=id).delete()
    
    return HttpResponseRedirect(reverse("myorders"))

def taskmanager(request):
    # dailyTasks is a dictionary, key = date, value = Object<summary = dictionary<breadType, count>, orders = List(Orders)>
    # 
    class ordersAndSummary:
        orders = []
        summary = {}
    todoOrders = Orders.objects.filter(deliveryTime__gte=  datetime.now().date()+ timedelta(days=2))
    todoDates = set()
    dailyTasks = {}
    for order in todoOrders:
        todoDates.add(order.deliveryTime.date()- timedelta(days=2))
    todoDates = list(todoDates)
    #
    #
    for date in todoDates:
        newOrdersAndSummary = ordersAndSummary()
        dailySummaryBread = {}
        for order in Orders.objects.filter(deliveryTime =  date + timedelta(days=2)):
            if order.breadType in dailySummaryBread:
                countTemp = dailySummaryBread[order.breadType]
                dailySummaryBread[order.breadType]=order.quantity+countTemp
            else:
                dailySummaryBread[order.breadType]=order.quantity
        newOrdersAndSummary.summary=dailySummaryBread
        newOrdersAndSummary.orders =Orders.objects.filter(deliveryTime =  date + timedelta(days=2))
        dailyTasks[date] = newOrdersAndSummary
    
    
    
    return render(request, "bakery/taskmanager.html", {
        "todoOrders": todoOrders,
        "todoDates": todoDates,
        "dailyTasks":dailyTasks,

    })

def metrics(request):
    # calculate total number of orders for every user
    #
    userMetrics = {}
    for user in User.objects.filter(is_superuser=False).all():
        # sum bread orders for evry user
        # sum cancelations for every user
        #
        totalOrders = Orders.objects.filter(owner=user).aggregate(Sum('quantity'))['quantity__sum']
        if totalOrders == None:
            totalOrders = 0
        canc = user.cancelations
        if canc == None:
            canc = 0
        dictValues = [totalOrders, canc]
        userMetrics[user]=dictValues

    return render(request, "bakery/metrics.html", {
        "users": userMetrics
    })

def blogadmin(request):
    return render(request, "bakery/blogadmin.html", {})