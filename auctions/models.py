from django.contrib.auth.models import AbstractUser
from django.db import models

#timestamps for listings etc?
class User(AbstractUser):
    #profile pic
    watchlist_item = models.ManyToManyField('Listings', related_name="watchlist_users")
#model for auction listings
class Listings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_listings")
    item = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # Date_listed = models.DateTimeField(auto_now=False, auto_now_add=False)
    # Not sure about how this works with the countdown timer just yet
    # Bid_end_time = models.DateTimeField(auto_now=False, auto_now_add=False)
    description = models.TextField()
    category = models.CharField(max_length=50)
    image = models.ImageField(upload_to='listings_images/', default='listings_images/noImage.jpg')
    image_url = models.URLField(blank=True, null=True, default='https://example.com/default-avatar.png')
    duration = models.IntegerField()
    def __str__(self):
        return f"{self.item} - ${self.price}"
# Model for auction bids
class Bids(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bids")
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="listing_bids")
    no_bids = models.IntegerField()
    current_bid = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f"Current bid is: {self.current_bid}"
    # Need to do more research into how this timer will work
    # Count_down = models.IntegerField() set this up in JS
# Model for comments on each listing
class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="listing_comments")
    comment = models.TextField()
    def __str__(self):
        return f"{self.comment}"
# Model for users history of closed/sold listings and the listings that a user has won/bought
class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_history")
    # Listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="listing_history")
    listing = models.CharField(max_length=64)
    listing_id = models.IntegerField(null=True)
    transaction_type = models.CharField(max_length=10)  # 'sold' or 'bought'
    def __str__(self):
        return f"{self.listing} was {self.transaction_type} by {self.user}"
    # Other fields for tracking history
    