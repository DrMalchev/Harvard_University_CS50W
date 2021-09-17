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
    #watchlist = Watchlist.objects.all()
    watch_owner = Watchlist.objects.filter(cross_id=listing_id).all()
    
    
    bid_message = "Add your bid here."

    new_bid=Bids.objects.all()
    comment=Comments.objects.filter(comment_for_id=listing_id).all()
    #comment.save()
    
    all_id_list = list(Watchlist.objects.filter(owner=request.user).all().values_list('cross_id', flat=True)) 
    all_bids_list = list(Bids.objects.all().values_list('desired_bid', flat=True)) 

    
    comment_form = AddCommentForm()
    bid_form = AddBidForm()

    if listing_id in all_id_list:
            is_in_watchlist=True
    else:
            is_in_watchlist=False

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
                    owner = request.user
                    )
                    new_bid.save()
                    listing.starting_bid = new_bid.desired_bid  
                    listing.save()
                    bid_message = "Bid accepted"
                else:
                    bid_message = "Bid not accepted"
                    #listing.starting_bid=999
                    listing.save()
                
        
        
        return render(request, "auctions/edit_listing.html", {
            "listing": listing,
            "comment_form": comment_form,
            "comments": comment,
            "bid_form": bid_form,
            "bid_message": bid_message,
            "all_bids":all_bids_list,
            "new_bid": new_bid,
            "postparams":postparams
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
        "is_in_watchlist": is_in_watchlist
        })
    
    
        # in watchlist
        # render "auctions/add_to_watchlist.html"
          
        
        comment_form = AddCommentForm()
        bid_form = AddBidForm()
        if request.user in Watchlist.objects.filter(owner = request.user, cross_id =listing_id).all():
        # if this user added item to watchlist 

            
            if request.method == 'POST' :

                postparams = request.readline()
                #parmod = str(request.readline())

                if 'comment' in str(postparams):
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

            


                else:
                    bid_form = AddBidForm(request.POST)
                    all_bids_list = list(Bids.objects.all().values_list('desired_bid', flat=True))  
                    all_bids_list = [float(i) for i in all_bids_list ]
                    if bid_form.is_valid() and bid_form.cleaned_data['form_bid']:
                        if bid_form.cleaned_data['form_bid'] > listing.starting_bid:
                            new_bid = Bids.objects.create(
                            desired_bid=bid_form.cleaned_data['form_bid'],
                            owner = request.user
                            )
                            new_bid.save()
                            listing.starting_bid = new_bid.desired_bid  
                            listing.save()
                            bid_message = "Bid accepted"
                        else:
                            bid_message = "Bid not accepted"
                            #listing.starting_bid=999
                            listing.save()
                
        
        
                return render(request, "auctions/add_to_watchlist.html", {
                "listing": listing,
                "comment_form": comment_form,
                "comments": comment,
                "bid_form": bid_form,
                "bid_message": bid_message,
                "all_bids":all_bids_list,
                "new_bid": new_bid,
                "postparams":postparams,
                "watch_owner":watch_owner
                })
            else:
                return render(request, "auctions/add_to_watchlist.html", {
                "listing": listing,
                "comment_form": comment_form,
                "comments": comment,
                "bid_form": bid_form,
                "bid_message": bid_message,
                "watch_owner":watch_owner
        
                })
    
        else:
            #item is in watchlist but was added by another user
            # render edit page
            return render(request, "auctions/edit_listing.html", {
                "listing": listing,
                "comment_form": comment_form,
                "comments": comment,
                "bid_form": bid_form,
                "bid_message": bid_message,
                "all_bids":all_bids_list,
                "new_bid": new_bid,
                
                "watch_owner":watch_owner
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

