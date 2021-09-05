from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.db import models
from djmoney.models.fields import MoneyField


class User(AbstractUser):
    id = models.AutoField(primary_key=True)


class Genre(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64)
    description = models.TextField(max_length=1024)

    def __str__(self):
        return f"{self.name}"


class Album(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=128)
    artist = models.CharField(max_length=64)
    year = models.CharField(max_length=4)
    description = models.TextField(max_length=1024)
    seller = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="albums_selling")
    image_url = models.URLField(max_length=200, blank=True)
    genres = models.ManyToManyField(
        Genre, blank=True, related_name="albums", help_text="Hold Command/Control Key to Select Multiple Genres")
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_closed = models.DateTimeField(blank=True, null=True)
    initial_price = MoneyField(
        default=0, max_digits=6, decimal_places=2, default_currency='USD')
    top_bid = MoneyField(
        max_digits=6, decimal_places=2, default_currency='USD', blank=True, null=True)
    top_bidder = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="winning", blank=True, null=True)
    watchers = models.ManyToManyField(
        User, blank=True, related_name="watchlist")

    def __str__(self):
        return f"{self.title} - {self.artist}"


class Bid(models.Model):
    id = models.AutoField(primary_key=True)
    album = models.ForeignKey(
        Album, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bids")
    amount = MoneyField(
        max_digits=6, decimal_places=2, default_currency='USD')

    def __str__(self):
        return f"{self.bidder} bid {self.amount} on {self.album}"


class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    album = models.ForeignKey(
        Album, on_delete=models.CASCADE, related_name="comments")
    commenter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField(max_length=1024)
    datetime_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.commenter} on {self.album}: {self.text}"
