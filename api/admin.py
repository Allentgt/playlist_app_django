from django.contrib import admin


# Register your models here.
from .models import Game, Playlist

admin.site.register(Game)
admin.site.register(Playlist)
