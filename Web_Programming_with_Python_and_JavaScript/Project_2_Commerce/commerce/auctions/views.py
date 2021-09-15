from django.contrib.auth.models import update_last_login
from auctions.forms import AddListingForm
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .models import Listings, User, Bids, Comments, Watchlist
from django.contrib.auth.decorators import login_required

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

    return render(request, "auctions/view_listing.html", {
        "listing": listing

    })

@login_required
def edit_listing(request, listing_id):
    listing = Listings.objects.get(pk=listing_id)

    return render(request, "auctions/edit_listing.html", {
        "listing": listing

    })
@login_required
def add_to_watchlist(request, listing_id):
    #saved_item_id = int(request.POST["saved_item"])
    listing = get_object_or_404(Listings, pk=listing_id)
    
   # watchlist, created = Watchlist.objects.get_or_create(
   #     owner=request.user
    #)

    watchlist = Watchlist.objects.create(
        owner=request.user,
        saved_item = listing.title
    )

    watchlist.save()

    return render(request, "auctions/add_to_watchlist.html", {
        "listing": listing,
       "watchlist":watchlist.saved_item

    })

@login_required
def remove_from_watchlist(request, listing_id):

    
    listing = Listings.objects.get(pk=listing_id)
    to_delete = get_object_or_404(Watchlist, saved_item=listing)
    to_delete.delete()
    

    
    return render(request, "auctions/remove_from_watchlist.html", {
        "listing": listing
        })
       
@login_required
def watchlist(request):
    
    watchlist = Watchlist.objects.all()
    length = range(len(watchlist))
    
    new_list=[]
    for i in length:
        new_list.append(watchlist[i].saved_item)

    
    return render(request, "auctions/watchlist.html", {
       "watchlist":new_list,
       "len": length

       
        
        })