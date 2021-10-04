from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, MyPosts
from datetime import datetime
from network.forms import AddPostForm


def index(request):
    return render(request, "network/index.html", {"allPosts": MyPosts.objects.order_by('-timestamp').all()})


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


def profile_page(request):
    user = request.user
    followingCount = User.objects.exclude(username = request.user).all().count()

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
        "posts": MyPosts.objects.filter(postUser=request.user).order_by('-timestamp').all(),
        "params": request.readline()
        
        })