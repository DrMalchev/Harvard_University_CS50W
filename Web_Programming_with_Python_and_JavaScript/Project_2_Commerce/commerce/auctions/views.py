from django.contrib.auth.models import update_last_login
from auctions.forms import AddBidForm, AddCommentForm, AddListingForm
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
from collections import defaultdict

def index(request):

    if Bids.objects.filter(winner_id=request.user.id).count() > 0 and Listings.objects.filter(active=False).count() > 0:
        won_item = Listings.objects.get(active=False)
        won_item_id=won_item.id
        
        return render(request, "auctions/index.html", {
        "Listings": Listings.objects.filter(active=True).all(),
        "user": request.user,
        "we_have_winner": True,
        "won_item_id":won_item_id,
        "won_item": won_item.title
        })
    else:

        return render(request, "auctions/index.html", {
        "Listings": Listings.objects.filter(active=True).all(),
        "user": request.user,
        "we_have_winner": False
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
            comment = "dummy",
            owner=request.user,
            active=True
            )

            listing.save()
                
            return HttpResponseRedirect(reverse("index"))

    
    else:
        form = AddListingForm()

        return render(request, 'auctions/add_listing.html', {'form': form})
    
def view_listing(request, listing_id):
    listing = Listings.objects.get(pk=listing_id, active=True)
    comment=Comments.objects.filter(comment_for_id=listing_id).all()
    active = listing.active

    return render(request, "auctions/view_listing.html", {
        "listing": listing,
        "comments": comment,
        "active": active

    })

@login_required
def edit_listing(request, listing_id):
    listing = Listings.objects.get(pk=listing_id)
    #watchlist = Watchlist.objects.all()
    watch_owner = Watchlist.objects.filter(cross_id=listing_id).all()
    active = listing.active
    
    bid_message = "Add your bid here."

    new_bid=Bids.objects.all()
    comment=Comments.objects.filter(comment_for_id=listing_id).all()
    #comment.save()
    
    all_id_list = list(Watchlist.objects.filter(owner=request.user).all().values_list('cross_id', flat=True)) 
    all_bids_list = list(Bids.objects.all().values_list('desired_bid', flat=True)) 

    
    comment_form = AddCommentForm()
    bid_form = AddBidForm()

    #is listing in watchlist
    if listing_id in all_id_list:
            is_in_watchlist=True
    else:
            is_in_watchlist=False

    #is this the user who created the listing
    
    if Listings.objects.filter(pk=listing_id, owner=request.user).all():
        is_owner = True
    else:
        is_owner=False

    if request.method == 'POST' :

        postparams = request.readline()
        
        if 'comment' in str(postparams):
            #Submitted form: Comment

            form = AddCommentForm(request.POST)
            if form.is_valid():

                comment=Comments.objects.create(
                    owner = request.user,
                    comment=form.cleaned_data['comment'],
                    time = datetime.now().replace(microsecond=0),
                    comment_for_id=listing_id
                    )
                comment.save()
                comment=Comments.objects.filter(comment_for_id=listing_id).all()

            


        else:
            # Submitted form: Add Bid

            bid_form = AddBidForm(request.POST)
            all_bids_list = list(Bids.objects.all().values_list('desired_bid', flat=True))  
            all_bids_list = [float(i) for i in all_bids_list ]
            if bid_form.is_valid() and bid_form.cleaned_data['form_bid']:
                if bid_form.cleaned_data['form_bid'] > listing.starting_bid:
                    new_bid = Bids.objects.create(
                    desired_bid=bid_form.cleaned_data['form_bid'],
                    owner = request.user,
                    winner_id=request.user.id,
                    won_item_id=listing_id
                    )
                    new_bid.save()
                    listing.starting_bid = new_bid.desired_bid  
                    listing.save()
                    bid_message = "Bid accepted"
                else:
                    bid_message = "Bid not accepted"
                    #listing.starting_bid=999
                    listing.save()
                
        
        # render after one of the forms is submitted
        return render(request, "auctions/edit_listing.html", {
            "listing": listing,
            "comment_form": comment_form,
            "comments": comment,
            "bid_form": bid_form,
            "bid_message": bid_message,
            "all_bids":all_bids_list,
            "new_bid": new_bid,
            "postparams":postparams,
            "is_owner": is_owner
            })

    else:
        #request is not POST

        return render(request, "auctions/edit_listing.html", {
        "listing": listing,
        "comment_form": comment_form,
        "comments": comment,
        "bid_form": bid_form,
        "bid_message": bid_message,
        "watch_owner": watch_owner,
        "is_in_watchlist": is_in_watchlist,
        "is_owner": is_owner,
        "active": active
        })
    
    

@login_required
def add_to_watchlist(request, listing_id):
    listing = Listings.objects.get(pk=listing_id)
    watchlist = Watchlist.objects.all()

    if listing_id not in Watchlist.objects.filter(owner=request.user, cross_id=listing_id).all():
        #if item not in watchlist for this user

        watchlist = Watchlist.objects.create(
            owner = request.user,
            saved_item = listing.title,
            cross_id = listing_id,
            image_url = listing.image_url,
            price = listing.starting_bid
            )

    return HttpResponseRedirect(reverse("edit_listing", args=(listing_id,)))

    

    

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

    #if request.user in Watchlist.objects.filter(owner = request.user).all():
        #if this user added item to watchlist
    watchlist =  Watchlist.objects.filter(owner = request.user).all()
    
    for item in Watchlist.objects.all().reverse():
        if Watchlist.objects.filter(cross_id=item.cross_id).count() > 1:
            item.delete()

                       
                       
    return render(request, "auctions/watchlist.html", {
       "watchlist":watchlist,
        })

@login_required
def close(request, listing_id):
    Listings.objects.filter(pk=listing_id).update(active=False)
    

    return HttpResponseRedirect(reverse("index"))

def categories(request):
    
    categories_temp = list(Listings.objects.filter(active=True).all().values_list('category', flat=True)) 

    categories = list(dict.fromkeys(categories_temp))

    return render(request, "auctions/categories.html", {
       "categories": categories
        })

def cat_display(request, cat_display):
   
    

    return render(request, "auctions/cat_display.html", {
        "Listings": Listings.objects.filter(active=True, category=cat_display).all(),
        "user": request.user,
        "we_have_winner": False,
        "category":cat_display
        })