from typing import Text
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, MyPosts, Following
from datetime import datetime
from network.forms import AddPostForm
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import json

@csrf_exempt
def index(request):

    paginator = Paginator(MyPosts.objects.order_by('-timestamp').all(), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    #user = User.objects.filter(username=request.User)
   # rawData = json.loads(request.body, strict=False)
    #data = rawData("data")

    return render(request, "network/index.html", {
        'page_obj': page_obj,
        'user': request.user,
        #'data':rawData
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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")






def new_post(request):

    if request.method == 'POST':
        form = AddPostForm(request.POST)
        if form.is_valid():
            myPost = MyPosts.objects.create(
                postUser = request.user,
                postBody = form.cleaned_data['body'],
                timestamp = datetime.now(),
                postLikes = 0

            )
            myPost.save()
            return HttpResponseRedirect(reverse("index"))
    else: #reuqest is not post => render the form
        form = AddPostForm()
        return render(request, 'network/new_post.html', {'form': form})

#temporary end

@csrf_exempt
def profile_page(request):

    
    user = request.user
    followingCount = Following.objects.filter(owner=request.user).values_list('following').distinct().count()
    followingList = list(Following.objects.filter(owner=request.user).values_list('following', flat=True))
    #followingList = ["tom", "jerry"]
    
    followersCount=Following.objects.filter(following=request.user).values_list('followers').count()


    #followersCount = User.followers.count()
    if request.method == 'POST':
    
        return render(request, "network/profile_page.html", {
        "user": user,
        "userObj": User.objects.exclude(username = request.user).all(),
        "followingCount": followingCount,
        "posts": MyPosts.objects.filter(postUser=request.user).order_by('-timestamp').all(),
        "params": request.readline()
        
        })
    else:
        return render(request, "network/profile_page.html", {
        "user": user,
        "userObj": User.objects.exclude(username = request.user).all(),
        "followingCount": followingCount,
        "followersCount": followersCount,
        "posts": MyPosts.objects.filter(postUser=request.user).order_by('-timestamp').all(),
        "params": request.readline(),
        "followingList": followingList
        })

def following(request):
    usersIFollow = list(Following.objects.filter(owner=request.user).values_list('following', flat=True))
    allPosts = []
    for usr in usersIFollow:
        for post in MyPosts.objects.all():
            if post.postUser.username == usr:
                allPosts.append(post)

    paginator = Paginator(allPosts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/following.html", {'page_obj': page_obj})

def follow(request, follow):


    followingList = list(Following.objects.filter(owner=request.user).values_list('following', flat=True))

    if follow not in followingList:
        new = Following.objects.create(
            owner=request.user,
            following=follow,
            followers=""
        )
        new.save()
    else:
        Following.objects.all().filter(following=follow).delete()
        # for item in Following.objects.all():

        #     if item.following == follow:
        #         item.following == "dummy"

    return HttpResponseRedirect(reverse("profile_page"))

@csrf_exempt
def edit(request, pk):
   # user = User.objects.filter(username=request.User)
    rawData = json.loads(request.body, strict=False)
    

    data = rawData["data"]
    myPost = MyPosts.objects.get(postUser=request.user, pk = pk)
    myPost.postBody = data
    myPost.timestamp = datetime.now()

            
    myPost.save()
    return HttpResponseRedirect(reverse("index"))

@csrf_exempt
def like(request, pk):
   # user = User.objects.filter(username=request.User)
    rawData = json.loads(request.body, strict=False)
    

    data = rawData["data"]
    myPost = MyPosts.objects.get(pk = pk)
    myPost.like = data
    if (data=="1"):
        myPost.postLikes+=1
    else:
        myPost.postLikes-=1
    myPost.save()
    return HttpResponseRedirect(reverse("index"))