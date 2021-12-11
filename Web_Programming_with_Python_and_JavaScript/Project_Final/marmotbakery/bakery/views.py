
from django.template.context_processors import csrf
from django.contrib.auth.decorators import user_passes_test
from collections import OrderedDict
from collections import defaultdict
import json
from .models import Blog, Content, User, Orders, Image
from bakery.forms import EditForm, PlaceOrderForm, FileForm
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
from types import SimpleNamespace
register = template.Library()


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
                # if user has not ordered bread for 2-3 days. but it is not empty db so app gets lastdate
                # from db and ques. but we need 2 days to deliver, so it should be corrected with +2 days
            elif Orders.objects.all().count() is not 0 and Orders.objects.order_by('-deliveryTime').latest('deliveryTime').deliveryTime.date() < datetime.now().date() + timedelta(days=2):
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
            # and has to be corrected to the last cummulative value
            if cumuTemp is None:
                cumuTemp = Orders.objects.last().cumulative

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
                Orders.objects.all().update(processed=1)

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
    # ifAccepted = False
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


@login_required
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
        # sorted(summaryByType.items(), key=lambda x: x[1], reverse=True)
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


@login_required
def edit(request, id):
    #
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
                # cumulative = newCumulative
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


@login_required
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
        user.cancelations += 1
        user.save()
    Orders.objects.filter(pk=id).delete()

    return HttpResponseRedirect(reverse("myorders"))


@user_passes_test(lambda u: u.is_superuser)
def taskmanager(request):
    # dailyTasks is a dictionary, key = date, value = Object<summary = dictionary<breadType, count>, orders = List(Orders)>
    #
    class ordersAndSummary:
        orders = []
        summary = {}
    todoOrders = Orders.objects.filter(
        deliveryTime__gte=datetime.now().date() + timedelta(days=2))
    todoDates = set()
    dailyTasks = {}
    for order in todoOrders:
        todoDates.add(order.deliveryTime.date() - timedelta(days=2))
    todoDates = list(todoDates)
    #
    #
    for date in todoDates:
        newOrdersAndSummary = ordersAndSummary()
        dailySummaryBread = {}
        for order in Orders.objects.filter(deliveryTime=date + timedelta(days=2)):
            if order.breadType in dailySummaryBread:
                countTemp = dailySummaryBread[order.breadType]
                dailySummaryBread[order.breadType] = order.quantity+countTemp
            else:
                dailySummaryBread[order.breadType] = order.quantity
        newOrdersAndSummary.summary = dailySummaryBread
        newOrdersAndSummary.orders = Orders.objects.filter(
            deliveryTime=date + timedelta(days=2))
        dailyTasks[date] = newOrdersAndSummary

    return render(request, "bakery/taskmanager.html", {
        "todoOrders": todoOrders,
        "todoDates": todoDates,
        "dailyTasks": dailyTasks,

    })


@user_passes_test(lambda u: u.is_superuser)
def metrics(request):
    # calculate total number of orders for every user
    #
    userMetrics = {}
    for user in User.objects.filter(is_superuser=False).all():
        # sum bread orders for evry user
        # sum cancelations for every user
        #
        totalOrders = Orders.objects.filter(owner=user).aggregate(
            Sum('quantity'))['quantity__sum']
        if totalOrders == None:
            totalOrders = 0
        canc = user.cancelations
        if canc == None:
            canc = 0
        dictValues = [totalOrders, canc]
        userMetrics[user] = dictValues
    #
    # Order metrics
    #
    # get all orders by bread type
    #
    thisOrders = {}
    for order in Orders.objects.all():
        if order.breadType in thisOrders:
            thisOrders[order.breadType] = order.quantity + \
                thisOrders[order.breadType]
        else:
            thisOrders[order.breadType] = order.quantity
    thisOrders = OrderedDict(
        sorted(thisOrders.items(), key=lambda k: k[1], reverse=True))
    #
    # get all orders for the current month
    #
    currentMonth = datetime.now().strftime("%B")
    currentOrders = {}
    for order in Orders.objects.filter(orderTime__month=datetime.now().month):
        if order.breadType in currentOrders:
            currentOrders[order.breadType] = order.quantity + \
                currentOrders[order.breadType]
        else:
            currentOrders[order.breadType] = order.quantity
    currentOrders = OrderedDict(
        sorted(currentOrders.items(), key=lambda k: k[1], reverse=True))

    return render(request, "bakery/metrics.html", {
        "users": userMetrics,
        "thisOrders": thisOrders,
        "currentOrders": currentOrders,
        "currentMonth": currentMonth
    })


@user_passes_test(lambda u: u.is_superuser)
def blogadmin(request):

    if Blog.objects.all():
        return render(request, "bakery/blogadmin.html", {
            "images": Image.objects.all(),
        })
    else:
        return render(request, "bakery/blogadmin.html", {
            "images": Image.objects.all(),
            "id": 0
        })


@user_passes_test(lambda u: u.is_superuser)
def deleteuser(request, id):
    # get data from JS fetch POST
    #

    User.objects.filter(pk=id).delete()
    return HttpResponseRedirect(reverse("metrics"))


def blog(request):
    return render(request, "bakery/blog.html", {
        "blog": Blog.objects.all(),
    })


def fileupload(request, id):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            initial_obj = Image(file=request.FILES['file'])
            initial_obj.filename = initial_obj.file.name
            initial_obj.filepath = initial_obj.file.url
            initial_obj.blogid = id
            initial_obj.save()
            return HttpResponseRedirect("/blogadmin")
    else:
        form = FileForm()
        return render(request, 'bakery/fileupload.html', {
            'id': id,
            'form': form
        })


def contententry(request, blogid):
    if request.method == "POST":
        body = request.body
        body=json.loads(request.body)
        for key, value in body.items():
            Content.objects.update_or_create(
                content=value,
                blogid=blogid,
                number=key
            )
        #newentry.save()
    return render(request, "bakery/blog.html", {
        "blog": Blog.objects.all(),
        "test": request.body
    })

    
