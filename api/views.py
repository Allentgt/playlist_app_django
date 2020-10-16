import simplejson as json
import random
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .models import Playlist, Game
from .forms import PlaylistForm, GameForm, GameListForm, PlaylistSubmissionFormSet


def index(request):
    return render(request, 'index.html')


def thanks(request):
    return render(request, 'thanks.html')


def create_game(request):
    if request.method == 'POST':
        form = GameForm(request.POST)
        if form.is_valid():
            data = {'name': form.cleaned_data['name'],
                    'sample_size': form.cleaned_data['sample_size'],
                    'pool_size': form.cleaned_data['pool_size'],
                    'contestants': form.cleaned_data['contestants']}
            game = Game(**data)
            game.save()
            return HttpResponseRedirect('/api/put_playlist/')
    else:
        form = GameForm()

    return render(request, 'create_game.html', {'form': form})


def put_game_details(request):
    if request.method == 'POST':
        user_details = PlaylistForm(request.POST)

        if user_details.is_valid():
            user_details = user_details.cleaned_data
            pool_size = user_details['game'].pool_size
            request.session['name'] = user_details['name']
            request.session['game'] = user_details['game'].name
            request.session['pool_size'] = pool_size
            return HttpResponseRedirect('/api/put_playlist/')
    else:
        user_details = PlaylistForm()
    context = {
        'playlist': user_details
    }
    return render(request, 'playlist_step1.html', context)


def put_playlist(request):
    if request.method == 'POST':
        fs = PlaylistSubmissionFormSet(request.POST)
        if fs.is_valid():
            playlist_data = fs.cleaned_data
            for i in playlist_data:
                i['link'] = i['link'].replace('watch?v=', 'embed/')
            playlist = {i: j for i, j in zip(range(len(playlist_data)), playlist_data)}
            data = {
                'name': request.session.get('name'),
                'game': Game.objects.get(name=request.session.get('game')),
                'playlist': json.dumps(playlist)
            }
            p = Playlist(**data)
            p.save()
            return HttpResponseRedirect('/api/thanks/')
    else:
        fs = PlaylistSubmissionFormSet(initial=[dict()] * request.session.get('pool_size'))
    context = {
        'fs': fs
    }
    return render(request, 'playlist_step2.html', context)


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
        all_playlist[obj.name] = json.loads(obj.playlist)
    for idx, i in all_playlist.items():
        sampling = random.choices(list(i.values()), k=sample_size)
        sampling = [{idx: i} for i in sampling]
        all_random_sample.extend(sampling)
    random.shuffle(all_random_sample)
    for i in all_random_sample:
        for j, k in i.items():
            k['name'] = j
    all_random_sample = [list(i.values())[0] for i in all_random_sample]
    return render(request, 'carousel.html', {'context': all_random_sample})
