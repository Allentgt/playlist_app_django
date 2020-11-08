from django import forms
from .models import Game


class GameForm(forms.Form):
    name = forms.CharField(max_length=100)
    sample_size = forms.IntegerField()
    pool_size = forms.IntegerField()
    contestants = forms.IntegerField()


class GameListForm(forms.Form):
    game_list = forms.ModelChoiceField(queryset=Game.objects.filter(ready_to_play=1, is_over=0).order_by('id'),
                                       widget=forms.Select(attrs={'class': 'choices-play'}))
    game_code = forms.CharField(max_length=6)


class PlaylistForm(forms.Form):
    name = forms.CharField(max_length=100)
    game = forms.ModelChoiceField(queryset=Game.objects.filter(ready_to_play=0).order_by('name'),
                                  widget=forms.Select(attrs={'class': 'choices'}))
    playlist = forms.CharField(required=True)
