from django import forms

# from playlist_app_django.api.models import Game
from .models import Game


class PlaylistForm(forms.Form):
    name = forms.CharField(max_length=100)
    game = forms.ModelChoiceField(queryset=Game.objects.all().order_by('id'))
    song1 = forms.CharField(widget=forms.TextInput)
    song2 = forms.CharField(widget=forms.TextInput)
    song3 = forms.CharField(widget=forms.TextInput)
    song4 = forms.CharField(widget=forms.TextInput)
    song5 = forms.CharField(widget=forms.TextInput)
    song6 = forms.CharField(widget=forms.TextInput)
    song7 = forms.CharField(widget=forms.TextInput)
    song8 = forms.CharField(widget=forms.TextInput)
    song9 = forms.CharField(widget=forms.TextInput)
    song10 = forms.CharField(widget=forms.TextInput)


class GameForm(forms.Form):
    name = forms.CharField(max_length=100)
    sample_size = forms.IntegerField()
    contestants = forms.IntegerField()


class GameListForm(forms.Form):
    game_list = forms.ModelChoiceField(queryset=Game.objects.all().order_by('id'))
