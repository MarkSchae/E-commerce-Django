from django.http import JsonResponse
import json
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from itertools import zip_longest
from django.contrib import messages

from .models import User, Listings, Comments, Bids, History


class NewListingForm(forms.Form):
    title = forms.CharField(label="Title")
    description = forms.CharField(label="Description", widget=forms.Textarea)
    starting_bid = forms.DecimalField(max_digits=10, decimal_places=2, label="Starting Bid")
    category = forms.CharField(label="Category")
    duration = forms.IntegerField()
    image = forms.ImageField(label="Image", required=False)
    image_url = forms.URLField(label="ImageUrl", required=False)
    # need to research this 
#form for watchlist, new bids, comments
class NewBidForm(forms.Form):
    bid = forms.DecimalField(max_digits=10, decimal_places=2, label="Add Bid")

def default(request):
    bids = Bids.objects.all()
    listings = Listings.objects.all()
    zipped_data = zip_longest(bids, listings)
    
    return render(request, "auctions/default.html", {
    "active_listings": Listings.objects.all(),
    "zipped": zipped_data,
})
    
def index(request):
    if request.user.is_authenticated:
    # Display users watchlisted items, model isnt set up corerctly to store items in the watchlist
    # User = User.objects.all()
    # Watchlist_items = user.watchlist_item
        user = request.user
        # Retrive the history of the current logged in user
        user_history = user.user_history.all()
        watchlist_items = user.watchlist_item.all()
        bids = Bids.objects.all()
        listings = Listings.objects.all()
        zipped_data = zip_longest(bids, listings)
        
        # Create a list containing only unique categories
        active_listings = Listings.objects.all()
        unique_categories = []
        for listing in active_listings:
            if listing.category in unique_categories:
                continue
            else:
                unique_categories.append(listing.category)
                
        return render(request, "auctions/index.html", {
            "active_listings": Listings.objects.all(),
            "watchlist_items": watchlist_items,
            "historys": user_history,
            "unique_categories": unique_categories,
            "bids": Bids.objects.all(),
            "zipped": zipped_data,
        })
    else:
        messages.error(request, "You need to be registered to access this page.")
        return HttpResponseRedirect(reverse("register"))

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
    return HttpResponseRedirect(reverse("default"))


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
    
def new_listing(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            form = NewListingForm(request.POST)
            if form.is_valid():
                # Access the submitted form data using cleaned_data dictionary
                title = form.cleaned_data["title"]
                description = form.cleaned_data["description"]
                starting_bid = form.cleaned_data["starting_bid"]
                category = form.cleaned_data["category"]
                duration = form.cleaned_data["duration"]
                image = form.cleaned_data.get("image")
                image_url = form.cleaned_data.get("image_url")

                # Check if image field is empty, and set the default value if it is
                if image is None:
                    image = 'static/auctions/noImage.png'

                # Check if image_url field is empty, and set the default value if it is
                if not image_url:
                    image_url = 'static/auctions/noImage.png'

                listing = Listings(
                    user=request.user,
                    item=title,
                    description=description,
                    price=starting_bid,
                    category=category,
                    duration=duration,
                    image=image,
                    image_url=image_url
                )
                listing.save()
                return HttpResponseRedirect(reverse("index"))
                
            else:
                return render(request, "auctions/new_listing.html", {
                    "form": form
                })
        else:
            messages.error(request, "You need to be registered to access this page.")
            return HttpResponseRedirect(reverse("register"))
    else:
        return render(request, "auctions/new_listing.html",{
            "form": NewListingForm()
    })
       
def listing_page(request, listing_page):
    if request.method == "POST":
        if request.user.is_authenticated:
            user = request.user
            form = NewBidForm(request.POST)
            if form.is_valid():
                # Retrieve the corresponding Bids instance 
                # Must add check if bid exsists
                bids = Bids.objects.filter(listing=listing_page).order_by('-current_bid').first()

                new_bid = form.cleaned_data["bid"]
                if bids:
                    # Check that the bid is larger than the current_bid
                    if bids.current_bid >= new_bid:
                        listing = Listings.objects.get(id=listing_page)
                        return render(request, "auctions/current_listing.html", {
                            "form": form,
                            "listings": listing,
                            "error_message": "Your bid must be higher than the current highest bid.",
                        })
                    else:
                        listing = Listings.objects.get(id=listing_page)
                        # Increment the no_bids field by one
                        bids.no_bids = (bids.no_bids or 0) + 1
                        bids.current_bid = new_bid
                        bids.user = user
                        bids.listing = listing
                        # Save the updated Bids instance
                        bids.save()

                        return HttpResponseRedirect(reverse("index"))
                else:
                    bids = Bids()
                    listing = Listings.objects.get(id=listing_page)
                    bid = listing.price
                    if bid >= new_bid:
                        return render(request, "auctions/current_listing.html", {
                            "form": form,
                            "listings": listing,
                            "error_message": "Your bid must be higher than the current highest bid.",
                        })
                    else:                   
                        # Increment the no_bids field by one
                        bids.no_bids = (bids.no_bids or 0) + 1
                        bids.current_bid = new_bid
                        bids.user = user
                        bids.listing = listing
                        # Save the updated Bids instance
                        bids.save()

                        return HttpResponseRedirect(reverse("index"))
                    
            else:
                return render(request, "auctions/new_listing.html", {
                    "form": form
                })
        else:
            messages.error(request, "You need to be registered to access this page.")
            return HttpResponseRedirect(reverse("register"))
    else:
        try:
            listing = Listings.objects.get(id=listing_page)
        except Listings.DoesNotExist:
            # Handle the case where the listing doesn't exist
            listing = None  # Set a default value for 'listing'
            pass

        if listing:
            # Continue with rendering if the listing exists
            return render(request, "auctions/current_listing.html", {
                "listings": listing,
                "bids": listing.listing_bids.all(),
                "comments": listing.listing_comments.all(),
                "form": NewBidForm()
            })
        else:
            # Handle the case where the listing doesn't exist
            user = request.user
            if History.objects.filter(listing_id=listing_page, user=user).exists():
                message = "The auction is closed, and you won the bidding war!"
            else:
                message = "The auction is closed, and you lost the bidding war!"
            return render(request, "auctions/index.html", {
                "message": message,
            })
                  
def add_comment(request, listing_id):
    if request.method == "POST":
        data = json.loads(request.body)
        listing_id = data.get("listing_id")
        comment_text = data.get("comment_text")
        user = request.user

        # Retrive listing object
        listing_foreign = Listings.objects.get(id=listing_id)
        # Create a new comment instance and use the lsiting object to create a foreign key relationship
        comment = Comments()
        comment.user = user
        comment.listing = listing_foreign
        comment.comment = comment_text
        comment.save()

        # Return the new comment data as JSON response
        new_comment_data = {
            "success": True,
            "comment_text": comment.comment,  # Assuming the comment has a 'comment' field
            # Add other relevant comment data if needed (e.g., comment ID, created timestamp, etc.)
        }
        return JsonResponse(new_comment_data) 

    # Return a JSON response indicating failure
    return JsonResponse({"success": False})

def add_watchlist(request, listing_id):
    if request.method == "POST":
        data = json.loads(request.body)
        listing_id = data.get("listing_id")

        listing = Listings.objects.get(id=listing_id)
        # Get the current user
        user = request.user

        if listing in user.watchlist_item.all():
            # Listing is already in the watchlist, remove it
            user.watchlist_item.remove(listing)
        else:
            # Listing is not in the watchlist, add it
            user.watchlist_item.add(listing)

        # Return a JSON response indicating success
        return JsonResponse({"success": True})

    # Return a JSON response indicating failure
    return JsonResponse({"success": False})

def my_listings(request):
    # Display user created listings 
    user = request.user
    # Access the user's created listings using the foreigh key "user_listings"
    user_listings = user.user_listings.all()
    # Display listings that the user has open bid on
    # Access the bids made by the user
    user_bids = user.user_bids.all()
    # Access the listings associated with the user's bids  
    user_bid_listings = [bid.listing for bid in user_bids] # For each row/bid in user_bids append to the user_bid_listings list the listing that is linked to the bid via a foreign key(bid.listing_bids)
    # Access the current bid amount
    user_listing_bids = [bid.current_bid for bid in user_bids if bid.user == user]

    return render(request, "auctions/my_listings.html", {
        "user_listings": user_listings,
        "user_bid_listings": user_bid_listings,  
        "user_listing_bids": user_listing_bids
    })
   
def close_auction(request, listing_id):
    # User close the auction of thier created listing
    if request.method == "POST":
    # Get the user created listing that they want to close using the related name of the foreign key and the current user
        user = request.user
        # user_listing = user.user_listings.get(id=listing_id)
        # On button click or form submission close the auction
        # Retrieve the listing that is being closed
        listing = Listings.objects.get(id=listing_id)
        #print("hello")# Definitley running this code twice
        # Retrieve the user associated with selling/closing the listing
        # user = listing.user
        # Determine the winning user
        winning_bid = Bids.objects.filter(listing=listing).order_by('-current_bid').first()

        # Retrive the user associated with buying the listing
        # Announce winner
        # Find winnng user using highest bid and the relationship between bids and the user
        # Add listing to the winning users won items field which i must still create

        # Check if any bids actually exsits
        if winning_bid:
            # Retrieve the user with the winning bid
            winner_user = winning_bid.user
            
            # if winning_bid and winning_bid.user == user:
                # is_winner = True
            # else:
                # is_winner = False
            # message = 'Auction closed, you successfully won the item.' if is_winner else 'Auction closed, you were outbid'
            
            # Add the won listing item to the user's won items field in the history model
            history_buyer = History()
            history_buyer.user = winner_user
            history_buyer.listing = listing.item
            history_buyer.transaction_type = "bought"
            history_buyer.listing_id = listing_id

            # Save the changes to the winner's user model
            history_buyer.save()

            # Return a response indicating success or redirect to a relevant page
            # return HttpResponse("Auction closed. Winner declared and listing moved to user's won items.")
        # Retrive the user that sold the item
        
        # Add the closed/sold listing to the history model with the correct fields
            history_seller = History()
            history_seller.user = user
            history_seller.listing = listing.item
            history_seller.transaction_type = "sold"
            history_buyer.listing_id = listing_id
            # Save the changes to the history model
            history_seller.save()

            # Delete the listing
            listing.delete()
            
            # Prepare the data for JSON response
            response_data = {"success": True, "is_winner": is_winner, "message": message}

            # Return a JSON response
            return JsonResponse(response_data)
    
        
def category(request):
    # Create a list containing only unique categories
    active_listings = Listings.objects.all()
    unique_categories = []
    for listing in active_listings:
        if listing.category in unique_categories:
            continue
        else:
            unique_categories.append(listing.category)
            
        return render(request, "auctions/index.html", {
        # "active_listings": Listings.objects.all(),
        # "watchlist_items": watchlist_items,
        # "historys": user_history,
        "unique_categories": unique_categories,
    })

    # Alternatively, if you want to return JSON response as well
    # response_data = {
    #     'success': True,
    #     'is_winner': is_winner,
    #     'message': 'Auction closed successfully.' if is_winner else 'Auction closed.',
    # }
    # return JsonResponse(response_data)
def categories_items(request, categories_name):
    # Use the category_name passed in the URL to filter listings
    listings = Listings.objects.filter(category=categories_name)
    
    
    return render(request, "auctions/categories_items.html", {
        "listings": listings
    })
    
