from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("test", views.test, name="test"),
    path("listing/<int:album_id>", views.listing, name="listing"),
    path("bid", views.bid, name="bid"),
    path("close", views.close, name="close"),
    path("comment", views.comment, name="comment"),
    path("watchlist/<int:user_id>", views.watchlist, name="watchlist"),
    path("delete_from_watchlist",
         views.delete_from_watchlist, name="delete_from_watchlist"),
    path("add_to_watchlist",
         views.add_to_watchlist, name="add_to_watchlist"),
    path("albums/<int:user_id>", views.albums, name="albums"),
    path("genre/<str:genre_name>", views.genre, name="genre"),
]
