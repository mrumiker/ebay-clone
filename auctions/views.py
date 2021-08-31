from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm
from django.contrib import messages

from .models import Album, Bid, User, Genre


class AlbumForm(ModelForm):
    class Meta:
        model = Album
        fields = ['title', 'artist', 'year',
                  'description', 'image_url', 'genres', 'initial_price', 'seller']


class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['album', 'bidder', 'amount']


def index(request):
    active_listings = Album.objects.filter(datetime_closed=None)
    return render(request, "auctions/index.html", {
        "active_listings": active_listings
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


@login_required
def create(request):
    if request.method == 'POST':
        form = AlbumForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("index"))
        raise ValidationError("Something went wrong. Please try again.")
    return render(request, "auctions/create.html", {
        "album_form": AlbumForm(),
    })


def listing(request, album_id):
    album = Album.objects.get(id=album_id)
    genres = album.genres.all()
    watchers = album.watchers.all()
    watchersIds = []
    for watcher in watchers:
        watchersIds.append(watcher.id)
    return render(request, "auctions/listing.html", {
        "album": album,
        "genres": genres,
        "watchers": watchers,
        "watchersIds": watchersIds,
        "form": BidForm(),
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
        if (not len(previous_bids) and bid > initial_price) or (len(previous_bids) and bid > max(previous_bids)):
            form.save()
            messages.info(request, "Your bid was successful!")
        else:
            messages.info(
                request, "Your bid must be higher than the current price")
    else:
        messages.info(
            request, "Something went wrong. Please try your bid again.")

    return HttpResponseRedirect(reverse("listing", args=[album_id]))


@login_required
def add_to_watchlist(request, album_id, user_id):
    album = Album.objects.get(id=album_id)
    watcher = User.objects.get(id=user_id)
    album.watchers.add(watcher)
    return HttpResponseRedirect(reverse("listing", args=[album_id]))


@login_required
def delete_from_watchlist(request, album_id, user_id):
    album = Album.objects.get(id=album_id)
    watcher = User.objects.get(id=user_id)
    album.watchers.remove(watcher)
    return HttpResponseRedirect(reverse("listing", args=[album_id]))


def test(request):
    if request.method == 'POST':
        form = AlbumForm(request.POST)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("index"))
        raise ValidationError("Something went wrong. Please try again.")
    return render(request, "auctions/test.html", {
        "form": AlbumForm()
    })
