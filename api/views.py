import simplejson as json
import random
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from .models import Playlist, Game
from .forms import PlaylistForm, GameForm, GameListForm


def index(request):
    return render(request, 'index.html')


def thanks(request):
    return render(request, 'thanks.html')


def create_game(request):
    if request.method == 'POST':
        form = GameForm(request.POST)
        if form.is_valid():
            data = {'name': form.cleaned_data['name'], 'sample_size': form.cleaned_data['sample_size'],
                    'contestants': form.cleaned_data['contestants']}
            game = Game(**data)
            game.save()
            return HttpResponseRedirect('/api/put_playlist/')
    else:
        form = GameForm()

    return render(request, 'game.html', {'form': form})


def put_playlist(request):
    if request.method == 'POST':
        form = PlaylistForm(request.POST)
        if form.is_valid():
            playlist = {i: j for i, j in zip(range(10), [form.cleaned_data['song1'], form.cleaned_data['song2'],
                                                         form.cleaned_data['song3'], form.cleaned_data['song4'],
                                                         form.cleaned_data['song5'], form.cleaned_data['song6'],
                                                         form.cleaned_data['song7'], form.cleaned_data['song8'],
                                                         form.cleaned_data['song9'], form.cleaned_data['song10']
                                                         ])}
            data = {'name': form.cleaned_data['name'], 'game': Game.objects.get(name=form.cleaned_data['game']),
                    'playlist': json.dumps(playlist)}
            p = Playlist(**data)
            p.save()
            return HttpResponseRedirect('/api/thanks/')
    else:
        form = PlaylistForm()

    return render(request, 'playlist.html', {'form': form})


def get_games(request):
    if request.method == 'POST':
        form = GameListForm(request.POST)
        if form.is_valid():
            game = form.cleaned_data['game_list'].id
            return HttpResponseRedirect(f'/api/randomise/{game}/')
    else:
        form = GameListForm()
    return render(request, 'games.html', {'form': form})


def randomise(request, game):
    all_playlist = {}
    all_random_sample = []
    playlist = Playlist.objects.filter(game=game)
    sample_size = Game.objects.get(id=game).sample_size
    for obj in playlist:
        all_playlist[obj.id] = json.loads(obj.playlist)
    for idx, i in all_playlist.items():
        sampling = random.choices(list(i.values()), k=sample_size)
        sampling = [{idx: i} for i in sampling]
        all_random_sample.extend(sampling)
    random.shuffle(all_random_sample)
    return JsonResponse(all_random_sample, safe=False)
