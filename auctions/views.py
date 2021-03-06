from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm
from django.contrib import messages

from datetime import datetime, timezone

from .models import Album, Bid, Comment, User, Genre


class AlbumForm(ModelForm):
    class Meta:
        model = Album
        fields = ['title', 'artist', 'year',
                  'description', 'image_url', 'genres', 'initial_price', 'seller']


class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['album', 'bidder', 'amount']


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['album', 'commenter', 'text']


def is_new(time):
    return (datetime.now(timezone.utc) - time).total_seconds() < 48 * 3600


def index(request):
    albums = Album.objects.all()
    active_listings = []
    closed_listings = []
    for album in albums:
        album.new = is_new(album.datetime_created)
        if album.datetime_closed:
            closed_listings.append(album)
        else:
            active_listings.append(album)
    return render(request, "auctions/index.html", {
        "active_listings": reversed(active_listings),
        "closed_listings": sorted(closed_listings, key=lambda k: k.datetime_closed, reverse=True),
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
                "message": "Invalid username and/or password.",
                "no_prompt": True,
            })
    else:
        return render(request, "auctions/login.html", {
            "no_prompt": True,
        })


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
                "message": "Passwords must match.",
                "no_prompt": True,
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken.",
                "no_prompt": True,
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html", {
            "no_prompt": True,
        })


@login_required
def create(request):
    if request.method == 'POST':
        form = AlbumForm(request.POST)
        title = request.POST["title"]
        seller = request.POST["seller"]
        if form.is_valid():
            form.save()
            album_id = Album.objects.get(title=title, seller=seller).id
            messages.info(request, "Album Listed!")
            return HttpResponseRedirect(reverse("listing", args=[album_id]))
        raise ValidationError("Something went wrong. Please try again.")
    genres = Genre.objects.all()
    return render(request, "auctions/create.html", {
        "genres": sorted(genres, key=lambda genre: genre.name)
    })


def listing(request, album_id):
    album = Album.objects.get(id=album_id)
    genres = album.genres.all()
    watchers = album.watchers.all()
    comments = Comment.objects.filter(album=album)
    bids = album.bids.all()
    bid_amounts = []
    for bid in bids:
        bid_amounts.append(bid.amount.amount)
    if len(bid_amounts):
        max_bid = max(bid_amounts)
        max_bidder = Bid.objects.get(
            album=album, amount=(max_bid, "USD")).bidder
    else:
        max_bid = album.initial_price.amount
        max_bidder = album.seller

    return render(request, "auctions/listing.html", {
        "album": album,
        "genres": genres,
        "watchers": watchers,
        "comments": comments,
        "max_bid": max_bid,
        "max_bidder": max_bidder,
        "new": is_new(album.datetime_created),
    })


@login_required
def bid(request):
    form = BidForm(request.POST)
    album_id = request.POST["album"]
    bid = float(request.POST["amount_0"])
    album = Album.objects.get(id=album_id)
    initial_price = album.initial_price.amount
    album_bids = album.bids.all()
    previous_bids = []
    for album_bid in album_bids:
        previous_bids.append(album_bid.amount)
    if form.is_valid:
        if (not len(previous_bids) and bid > initial_price) or (len(previous_bids) and bid > max(previous_bids).amount):
            form.save()
            album.top_bid = bid
            album.top_bid_currency = 'USD'
            bidder_id = request.POST["bidder"]
            album.top_bidder = User.objects.get(id=bidder_id)
            album.save()
            messages.info(request, "Your bid was successful!")
        else:
            messages.info(
                request, "Your bid must be higher than the current price.")
    else:
        messages.info(
            request, "Something went wrong. Please try your bid again.")

    return HttpResponseRedirect(reverse("listing", args=[album_id]))


@login_required
def close(request):
    album_id = request.POST["album"]
    album = Album.objects.get(id=album_id)
    album.datetime_closed = datetime.now()
    album.save()
    messages.info(request, "Listing Closed!")
    return HttpResponseRedirect(reverse("listing", args=[album_id]))


@login_required
def comment(request):
    form = CommentForm(request.POST)
    album_id = request.POST["album"]
    if form.is_valid:
        form.save()
        messages.info(request, "Your Comment was Posted")
    else:
        messages.info(request, "Something went wrong. Please try again.")
    return HttpResponseRedirect(reverse("listing", args=[album_id]))


@login_required
def watchlist(request, user_id):
    user = User.objects.get(id=user_id)
    albums = Album.objects.all()
    active_listings = []
    closed_listings = []
    for album in albums:
        album.new = is_new(album.datetime_created)
        watchers = album.watchers.all()
        if user in watchers:
            if album.datetime_closed:
                closed_listings.append(album)
            else:
                active_listings.append(album)
    return render(request, "auctions/watchlist.html", {
        "active_listings": active_listings,
        "closed_listings": closed_listings,
        "watcher": user,
    })


@login_required
def add_to_watchlist(request):
    album_id = request.POST["album"]
    user_id = request.POST["user"]
    album = Album.objects.get(id=album_id)
    watcher = User.objects.get(id=user_id)
    album.watchers.add(watcher)
    messages.info(request, f"{album} added to Watchlist")
    return HttpResponseRedirect(reverse("listing", args=[album_id]))


@login_required
def delete_from_watchlist(request):
    album_id = request.POST["album"]
    user_id = request.POST["user"]
    album = Album.objects.get(id=album_id)
    watcher = User.objects.get(id=user_id)
    album.watchers.remove(watcher)
    messages.info(request, f"{album} removed from Watchlist")
    return HttpResponseRedirect(reverse("listing", args=[album_id]))


def albums(request, user_id):
    user = User.objects.get(id=user_id)
    albums_winning = user.winning.all()
    albums_won = list(
        filter(lambda album: album.datetime_closed, albums_winning))
    selling = user.selling.all()
    for album in albums_won:
        album.new = is_new(album.datetime_created)
    for album in selling:
        album.new = is_new(album.datetime_created)
    return render(request, "auctions/albums.html", {
        "won": albums_won,
        "selling": list(reversed(selling)),
        "featured_user": user,
    })


def genre(request, genre_name):
    genre = Genre.objects.get(name=genre_name)
    albums = Album.objects.filter(genres=genre)
    active_listings = []
    closed_listings = []
    for album in albums:
        album.new = is_new(album.datetime_created)
        if album.datetime_closed:
            closed_listings.append(album)
        else:
            active_listings.append(album)
    return render(request, "auctions/genre.html", {
        "genre": genre,
        "active_listings": list(reversed(active_listings)),
        "closed_listings": sorted(closed_listings, key=lambda k: k.datetime_closed, reverse=True),
    })


def all_genres(request):
    genres = Genre.objects.all()
    return render(request, "auctions/genres.html", {
        "genres": sorted(genres, key=lambda genre: genre.name)
    })


def search(request):
    search_str = request.POST["search_str"]
    albums = Album.objects.all()
    active_listings = []
    closed_listings = []
    for album in albums:
        album.new = is_new(album.datetime_created)
        if search_str.lower() in album.title.lower() or search_str.lower() in album.artist.lower():
            if album.datetime_closed:
                closed_listings.append(album)
            else:
                active_listings.append(album)
    return render(request, "auctions/search.html", {
        "search_str": search_str,
        "active_listings": list(reversed(active_listings)),
        "closed_listings": sorted(closed_listings, key=lambda k: k.datetime_closed, reverse=True),
    })
