from django.urls import path

from . import views

urlpatterns = [
    path("home", views.index, name="index"),
    path("", views.default, name="default"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_listing", views.new_listing, name ="new_listing"),
    path("my_listings", views.my_listings, name="my_listings"),
    path("<str:listing_page>/", views.listing_page, name="listing_page"),
    path("<str:listing_id>/comment", views.add_comment, name="comment"),
    path("<str:listing_id>/watchlist", views.add_watchlist, name="add_watchlist"),    
    path("<str:listing_id>/close_auction", views.close_auction, name="close_auction"),
    path("<str:categories_name>/categories_items", views.categories_items, name="categories_items"),
]
