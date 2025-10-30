# **Django E-commerce App**

## **Overview**

This is a full-featured online auction web application built with **Django**. Users can register, create listings, place bids, comment on listings, manage a watchlist, and track their auction history. Listings can be closed by the seller, with winning bids recorded in the history.

---

## **Features**

* **User Authentication:** Registration, login, and logout using Django's `AbstractUser`.
* **Auction Listings:** Users can create new listings with title, description, starting bid, category, duration, and optional image or image URL.
* **Bidding System:** Users can place bids on active listings. Bids are validated to ensure they are higher than the current highest bid.
* **Watchlist:** Users can add or remove listings from their personal watchlist.
* **Comments:** Users can comment on listings, supporting real-time feedback.
* **History Tracking:** Records listings sold or bought by each user.
* **Category Filtering:** Listings can be filtered by category.
* **Dynamic Pages:** Pages update with the current highest bids, watchlist items, and user history.

---

## **Project Structure**

```
auctions/
├── migrations/              # Django migration files
├── media/                  # Static assets (images, CSS, JS)
│   └── listings_images/
│       └── noImage.jpg
├── templates/
│   └── auctions/
│       ├── index.html
│       ├── login.html
│       ├── register.html
│       ├── new_listing.html
│       ├── current_listing.html
│       ├── my_listings.html
│       ├── categories_items.html
│       └── default.html
├── models.py                # Database models
├── views.py                 # View logic & forms
├── forms.py                 # Forms for new listings and bids
├── urls.py                  # URL routes
└── admin.py                 # Django admin registrations
```

---

## **Models**

### **User**

* Extends `AbstractUser`.
* Includes a **watchlist** (`ManyToManyField`) for saved listings.

### **Listings**

* Fields: `user`, `item`, `price`, `description`, `category`, `image`, `image_url`, `duration`.
* Represents an auction listing.

### **Bids**

* Fields: `user`, `listing`, `no_bids`, `current_bid`.
* Tracks the number of bids and the current highest bid for a listing.

### **Comments**

* Fields: `user`, `listing`, `comment`.
* Stores user comments on listings.

### **History**

* Fields: `user`, `listing`, `listing_id`, `transaction_type`.
* Tracks listings that were sold or bought by users.

---

## **Views**

* **index:** Homepage showing active listings, user watchlist, and user history.
* **default:** A default page rendering all listings and bids.
* **login_view / logout_view / register:** Handle user authentication.
* **new_listing:** Create a new auction listing.
* **listing_page:** View a single listing, place bids, and see comments.
* **add_comment:** Add a comment via AJAX.
* **add_watchlist:** Add or remove listing from watchlist via AJAX.
* **my_listings:** Display listings created by the user and their bids.
* **close_auction:** Close a listing and update transaction history.
* **category / categories_items:** List unique categories and filter listings by category.

---

## **Forms**

* **NewListingForm:** For creating listings (title, description, starting bid, category, duration, image, image_url).
* **NewBidForm:** For placing bids.

---

## **Setup Instructions**

1. **Clone the repository:**

   ```bash
   git clone <repository_url>
   cd <repository_folder>
   ```

2. **Install dependencies:**

   ```bash
   pip install django
   ```

3. **Apply migrations:**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create a superuser (optional, for admin access):**

   ```bash
   python manage.py createsuperuser
   ```

5. **Run the development server:**

   ```bash
   python manage.py runserver
   ```

6. **Access the application:**
   Open your browser and go to `http://127.0.0.1:8000/`.


---

## **Future Improvements**

* Implement countdown timers for auctions.
* Refactor bid handling to prevent race conditions in concurrent bidding.
* Add real-time updates using **WebSockets** or Django Channels.
* Enhance user interface for better usability and responsiveness.
* Optimize database queries for performance.
* Refactor client side request handling
