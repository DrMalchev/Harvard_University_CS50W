from django.contrib.auth.models import update_last_login
from auctions.forms import AddCommentForm, AddListingForm
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .models import Listings, User, Bids, Comments, Watchlist
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Max
from datetime import datetime
from django.db import models

def index(request):
    return render(request, "auctions/index.html", {
        "Listings": Listings.objects.all(),
        "user": request.user
        
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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def add_listing(request):
    

    if request.method == 'POST':
        
        form = AddListingForm(request.POST)
            
        if form.is_valid():

            if form.cleaned_data['image_url']!=None:
                image_assigned = form.cleaned_data['image_url']
            else:
                image_assigned = "No URL"

            listing = Listings.objects.create(
            title=form.cleaned_data['title'], 
            description=form.cleaned_data['description'], 
            category=form.cleaned_data['category'], 
            image_url=image_assigned, 
            starting_bid = form.cleaned_data['starting_bid'],
            new_bid = 0.01,
            comment = "dummy"
            )

            listing.save()
                
            return HttpResponseRedirect(reverse("index"))

    
    else:
        form = AddListingForm()

        return render(request, 'auctions/add_listing.html', {'form': form})
    
def view_listing(request, listing_id):
    listing = Listings.objects.get(pk=listing_id)
    comment=Comments.objects.filter(comment_for_id=listing_id).all()

    return render(request, "auctions/view_listing.html", {
        "listing": listing,
        "comments": comment

    })

@login_required
def edit_listing(request, listing_id):
    listing = Listings.objects.get(pk=listing_id)
    comment_form = AddCommentForm()

    
    comment=Comments.objects.filter(comment_for_id=listing_id).all()
    #comment.save()
    
    if request.method == 'POST':
        form = AddCommentForm(request.POST)
        if form.is_valid():

            comment=Comments.objects.create(
                comment=form.cleaned_data['comment'],
                owner = request.user,
                time = datetime.now().replace(microsecond=0),
                comment_for_id=listing_id
            )
            comment.save()
            comment=Comments.objects.filter(comment_for_id=listing_id).all()
            
                

    all_id_list = list(Watchlist.objects.all().values_list('cross_id', flat=True)) 
    
    if listing_id not in all_id_list:

        return render(request, "auctions/edit_listing.html", {
        "listing": listing,
        "comment_form": comment_form,
        "comments": comment
        
        })
    
    else:
        return render(request, "auctions/add_to_watchlist.html", {
        "listing": listing,
        "comment_form": comment_form,
        "comments":comment
        })

    
@login_required
def add_to_watchlist(request, listing_id):
    #saved_item_id = int(request.POST["saved_item"])
    listing = get_object_or_404(Listings, pk=listing_id)
    
    comment_form = AddCommentForm()

    
    comment=Comments.objects.filter(comment_for_id=listing_id).all()
    #comment.save()
    
    if request.method == 'POST':
        form = AddCommentForm(request.POST)
        if form.is_valid():

            comment=Comments.objects.create(
                comment=form.cleaned_data['comment'],
                owner = request.user,
                time = datetime.now().replace(microsecond=0),
                comment_for_id=listing_id
            )
            comment.save()
            comment=Comments.objects.filter(comment_for_id=listing_id).all()


    all_id_list = list(Watchlist.objects.all().values_list('cross_id', flat=True)) 
    
    if listing_id not in all_id_list:

        watchlist = Watchlist.objects.create(
            owner=request.user,
            saved_item = listing.title,
            cross_id=listing_id,
            image_url=listing.image_url,
            price=listing.starting_bid
            )

        watchlist.save()
    
        return render(request, "auctions/add_to_watchlist.html", {
        "listing": listing,
       "watchlist":watchlist.saved_item,
       "check": all_id_list,
       "comment_form": comment_form,
        "comments": comment

        })
    else:
        return render(request, "auctions/add_to_watchlist.html", {
            "listing":listing,
            "comment_form": comment_form,
            "comments": comment
            })
    

    

@login_required
def remove_from_watchlist(request, listing_id):

    listing = get_object_or_404(Listings, pk=listing_id)
    
    Watchlist.objects.filter(cross_id=listing_id).delete()
    
    
    return render(request, "auctions/remove_from_watchlist.html", {
        "listing": listing
        })
       
@login_required
def watchlist(request):
    
    watchlist = Watchlist.objects.all()
    length = range(len(watchlist))
     
    
    return render(request, "auctions/watchlist.html", {
       "watchlist":watchlist,
        })

""" @login_required
def comments(request, listing_id):
    listing = get_object_or_404(Listings, pk=listing_id)
    comment_form = AddCommentForm()
    comments= list(Comments.objects.all().values_list('comments', flat=True)) 
    return render(request, "auctions/edit_listing.html", {
        "listing": listing,
        "comment_form": comment_form,
        "comments":comments
        }) """