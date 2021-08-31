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
    path("delete_from_watchlist/<int:user_id>/<int:album_id>",
         views.delete_from_watchlist, name="delete_from_watchlist"),
    path("add_to_watchlist/<int:user_id>/<int:album_id>",
         views.add_to_watchlist, name="add_to_watchlist"),

]
