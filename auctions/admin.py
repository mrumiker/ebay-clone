from django.contrib import admin
from .models import User, Genre, Album, Bid, Comment

# Register your models here.
admin.site.register(User)
admin.site.register(Genre)
admin.site.register(Album)
admin.site.register(Bid)
admin.site.register(Comment)
