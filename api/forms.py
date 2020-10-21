from django import forms
from django.forms import formset_factory

from .models import Game


class PlaylistForm(forms.Form):
    name = forms.CharField(max_length=100)
    game = forms.ModelChoiceField(queryset=Game.objects.all().order_by('id'),
                                  widget=forms.Select(attrs={'class': 'choices'}))


class GameForm(forms.Form):
    name = forms.CharField(max_length=100)
    sample_size = forms.IntegerField()
    pool_size = forms.IntegerField()
    contestants = forms.IntegerField()


class GameListForm(forms.Form):
    game_list = forms.ModelChoiceField(queryset=Game.objects.filter(ready_to_play=1).order_by('id'),
                                       widget=forms.Select(attrs={'class': 'choices-play'}))


class PlaylistSubmissionForm(forms.Form):
    song_name = forms.CharField(required=True)
    link = forms.CharField(required=True)


PlaylistSubmissionFormSet = formset_factory(PlaylistSubmissionForm, extra=0)
