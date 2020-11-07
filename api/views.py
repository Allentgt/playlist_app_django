import ast
import os
import random
import re
import time
from functools import reduce
from math import gcd

from celery.result import AsyncResult
from pytube import Playlist as YTPlaylist
import simplejson as json
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .forms import PlaylistForm, GameForm, GameListForm
from .models import Playlist, Game
from playlist import settings
from .tasks import download_and_save_music_locally


def index(request):
    return render(request, 'index.html')


def terms_and_conditions(request):
    return render(request, 'tnc.html')


def game_info_howto(request):
    return render(request, 'gameinfo.html')


def about_us(request):
    return render(request, 'aboutus.html')


def feedback(request):
    return render(request, 'feedback.html')


def thanks(request):
    return render(request, 'thanks.html')


"""def create_game(request):
    if request.method == 'POST':
        try:
            form = GameForm(request.POST)
            if form.is_valid():
                data = {'name': form.cleaned_data['name'],
                        'sample_size': form.cleaned_data['sample_size'],
                        'pool_size': form.cleaned_data['pool_size'],
                        'contestants': form.cleaned_data['contestants']}
                game = Game(**data)
                game.save()
                return HttpResponseRedirect('/api/put_playlist/')
        except Exception as e:
            return JsonResponse({'message': str(e)})
    else:
        form = GameForm()

    return render(request, 'create_game.html', {'form': form})"""


@csrf_exempt
def create_game(request):
    try:
        name = request.POST.get('name')
        game_list = [game.name for game in Game.objects.all()]
        error = "Sorry, A game with the same name already exists ;)"
        if name in game_list:
            return JsonResponse({'status': 'FAILED', 'message': error})
        data = {
            'name': name,
            'sample_size': request.POST.get('sample_size'),
            'pool_size': request.POST.get('pool_size'),
            'contestants': request.POST.get('contestants')
        }
        game = Game(**data)
        game.save()
        response = {
            'status': 'SUCCESS',
            'message': 'Game Created'
        }
    except Exception as e:
        response = {
            'status': 'FAILED',
            'message': str(e)
        }
    return JsonResponse(response)


"""def put_playlist(request):
    if request.method == 'POST':
        try:
            playlist_details = PlaylistForm(request.POST)
            if playlist_details.is_valid():
                playlist_details = playlist_details.cleaned_data
                error = "Sorry, I guess you have a very common name ;)"
                username_list = [player_list.name for player_list in Playlist.objects.filter(game=playlist_details['game'])]
                if playlist_details['name'] in username_list:
                    return JsonResponse({'error': error})
                game_obj = Game.objects.get(name=playlist_details['game'])
                playlist_object = Playlist.objects.filter(game=game_obj)
                message = f'''Sorry {playlist_details["name"]}, You didn\'t make the cut :(\n
                May be try joining another game 
                or make better friends! '''
                if len(playlist_object) == game_obj.contestants:
                    return render(request, 'apology.html', {'message': message})
                playlist, jobs = {}, []
                pl = YTPlaylist(playlist_details["playlist"])
                for idx, link in enumerate(pl):
                    filename = f"{playlist_details['name'].lower()}_{playlist_details['game'].name.replace(' ', '_')}_{idx + 1}"
                    result = download_and_save_music_locally.delay(filename, link)
                    jobs.append(result.task_id)
                    all_songs = json.loads(game_obj.all_songs)
                    all_songs.append(link)
                    game_obj.all_songs = json.dumps(all_songs)
                    game_obj.save()
                    playlist[idx + 1] = os.path.join(f'{filename}.mp3')
                    time.sleep(3)
                data = {
                    'name': playlist_details['name'].lower(),
                    'game': game_obj,
                    'playlist': json.dumps(playlist)
                }
                p = Playlist(**data)
                p.save()
                playlist_object = Playlist.objects.filter(game=game_obj)
                if len(playlist_object) == game_obj.contestants:
                    game_obj.ready_to_play = 1
                    game_obj.save()
                return render(request, 'thanks.html', context={'jobs': jobs})
        except Exception as e:
            return JsonResponse({'message': str(e)})
    else:
        playlist_details = PlaylistForm()
    context = {
        'playlist': playlist_details
    }
    return render(request, 'playlist.html', context)"""


@csrf_exempt
def put_playlist(request):
    try:
        name = request.POST.get('name')
        game = request.POST.get('game')
        playlist = request.POST.get('playlist')
        game_obj = Game.objects.get(id=game)
        playlist_object = Playlist.objects.filter(game=game)

        error = "Sorry, I guess you have a very common name ;)"
        username_list = [player_list.name for player_list in playlist_object]
        if name in username_list:
            return JsonResponse({'status': 'FAILED', 'message': error})

        message = f"Sorry {name}, You didn't make the cut. May be try joining another game or make better friends!"
        if len(playlist_object) == game_obj.contestants:
            return JsonResponse({'status': 'FAILED', 'message': message})

        playlist_dict, error_data, jobs, duplicate_songs = {}, {}, [], []
        try:
            pl = YTPlaylist(playlist)
        except Exception as e:
            return JsonResponse({'status': 'FAILED', 'message': 'Invalid Playlist URL'})

        song_list = json.loads(game_obj.all_songs)
        for song in pl:
            if song in song_list:
                duplicate_songs.append(song)
        if duplicate_songs:
            error_data['duplicate'] = duplicate_songs

        game_pool_size = game_obj.pool_size
        playlist_length = len(pl)
        length_error = f"Sorry, Your playlist should be of length {game_pool_size}! ;)"
        if not playlist_length == game_pool_size:
            error_data['length'] = length_error
        if error_data:
            error_data['status'] = 'FAILED'
            return JsonResponse(error_data)

        for idx, link in enumerate(pl):
            filename = f"{name.lower().replace(' ', '_')}_{game.replace(' ', '_')}_{idx + 1}"
            result = download_and_save_music_locally.delay(filename, link)
            jobs.append(result.task_id)
            all_songs = json.loads(game_obj.all_songs)
            all_songs.append(link)
            game_obj.all_songs = json.dumps(all_songs)
            game_obj.save()
            playlist_dict[idx + 1] = os.path.join(f'{filename}.mp3')
        data = {
            'name': name.lower(),
            'game': game_obj,
            'playlist': json.dumps(playlist_dict)
        }
        p = Playlist(**data)
        p.save()
        playlist_object = Playlist.objects.filter(game=game)
        if len(playlist_object) == game_obj.contestants:
            game_obj.ready_to_play = 1
            game_obj.save()
        return JsonResponse({'status': 'SUCCESS', 'message': 'Playlist Submitted', 'jobs': jobs})
    except Exception as e:
        return JsonResponse({'status': 'FAILED', 'message': str(e)})


@csrf_exempt
def poll_download(request):
    try:
        jobs = ast.literal_eval(request.POST.get('jobs'))
        result = []
        for task in jobs:
            res = AsyncResult(task)
            result.append({'state': res.status, 'info': res.result})
        return JsonResponse({'result': result})
    except Exception as e:
        return JsonResponse({'message': str(e)})


def get_games(request):
    try:
        if request.method == 'POST':
            form = GameListForm(request.POST)
            if form.is_valid():
                game = form.cleaned_data['game_list'].id
                return HttpResponseRedirect(f'/api/randomise/{game}/')
    except Exception as e:
        return JsonResponse({'message': str(e)})
    else:
        form = GameListForm()
    return render(request, 'games.html', {'form': form})


def randomise(request, game):
    try:
        all_playlist = {}
        all_random_sample = []
        uniquePlayers = []
        playlist = Playlist.objects.filter(game=game)
        game_object = Game.objects.get(id=game)
        sample_size = game_object.sample_size
        scorecard = dict()
        for player in playlist:
            scorecard[player.name] = 0
        game_object.score = json.dumps(scorecard)
        game_object.save()
        for obj in playlist:
            all_playlist[obj.name] = json.loads(obj.playlist)
            uniquePlayers.append(obj.name)
        for idx, i in all_playlist.items():
            sampling = random.choices(list(i.values()), k=sample_size)
            sampling = [{idx: i} for i in sampling]
            all_random_sample.extend(sampling)
        random.shuffle(all_random_sample)
        result = []
        for i in all_random_sample:
            result.append({'name': list(i.keys())[0], 'link': list(i.values())[0]})
        return render(request, 'songs.html',
                      {'context': result, 'uniquePlayers': uniquePlayers, 'scorecard': scorecard})
    except Exception as e:
        return JsonResponse({'message': str(e)})


def lcm(denominators):
    return reduce(lambda a, b: a * b // gcd(a, b), denominators)


@csrf_exempt
def vote(request):
    try:
        game = request.POST.get('game')
        game_obj = Game.objects.get(id=game)
        scorecard = json.loads(game_obj.score)
        votes = json.loads(request.POST.get('votes'))
        answer = request.POST.get('answer')
        max_score = lcm([i + 1 for i in range(len(scorecard))])
        results = {player: 1 for player in scorecard if player in votes and votes[player] == answer}
        correct_answers = len(results)
        if correct_answers:
            round_score = max_score / correct_answers
            scorecard.update({player: scorecard[player] + round_score for player in results})
        else:
            round_score = max_score
            scorecard.update({player: scorecard[player] + round_score for player in scorecard if player == answer})
        game_obj.score = json.dumps(scorecard)
        game_obj.save()
        return JsonResponse(scorecard)
    except Exception as e:
        return JsonResponse({'message': str(e)})


@csrf_exempt
def find_duplicate_name(request):
    try:
        game = request.POST.get('game')
        player_name = request.POST.get('player_name')
        game_obj = Game.objects.get(id=game)
        error = """Sorry, I guess you have a very common name ;)"""
        username_list = [player_list.name for player_list in Playlist.objects.filter(game=game_obj)]
        if player_name in username_list:
            return JsonResponse({'message': error})
        else:
            return JsonResponse({'message': 'SUCCESS'})
    except Exception as e:
        return JsonResponse({'message': str(e)})


@csrf_exempt
def game_info(request):
    try:
        game = request.POST.get('game')
        game_obj = Game.objects.get(id=game)
        playlist_obj = Playlist.objects.filter(game=game_obj)
        response = {
            'contestants': [player.name for player in playlist_obj],
            'available_slots': game_obj.contestants - len(playlist_obj),
            'playlist_length': game_obj.pool_size
        }
        return JsonResponse(response)
    except Exception as e:
        return JsonResponse({'message': str(e)})


@csrf_exempt
def find_duplicate_game(request):
    try:
        name = request.POST.get('name')
        game_list = [game.name for game in Game.objects.all()]
        error = """Sorry, A game with the same name already exists ;)"""
        if name in game_list:
            return JsonResponse({'message': error})
        else:
            return JsonResponse({'message': 'SUCCESS'})
    except Exception as e:
        return JsonResponse({'message': str(e)})


@csrf_exempt
def send_support_mail(request):
    subject = request.POST.get('subject')
    body = request.POST.get('body')
    email = request.POST.get('email')
    support = settings.EMAIL_HOST_USER
    attachments = request.FILES.getlist('attachment')
    try:
        mail = EmailMessage(subject, body, email, [support])
        for attachment in attachments:
            mail.attach(attachment.name, attachment.read(), attachment.content_type)
        mail.send()
        return JsonResponse({'message': 'success'})
    except Exception as e:
        return JsonResponse({'message': str(e)})


@csrf_exempt
def playlist_validations(request):
    try:
        game = request.POST.get('game')
        link = request.POST.get('link')
        game_object = Game.objects.get(id=game)
        song_list = json.loads(game_object.all_songs)
        playlist = YTPlaylist(link)
        duplicate_songs = []
        error_data = {}
        for song in playlist:
            if song in song_list:
                duplicate_songs.append(song)
        if duplicate_songs:
            error_data['duplicate'] = duplicate_songs

        game_pool_size = game_object.pool_size
        playlist_length = len(playlist)
        length_error = f"Sorry, Your playlist should be of length {game_pool_size}! ;)"
        if not playlist_length == game_pool_size:
            error_data['length'] = length_error
        if error_data:
            error_data['status'] = 'FAILED'
            return JsonResponse(error_data)
        return JsonResponse({'status': 'SUCCESS'})
    except Exception as e:
        return JsonResponse({'message': str(e)})


@csrf_exempt
def end_game(request):
    try:
        list_of_winners = []
        game_obj = Game.objects.get(id=request.POST.get('game'))
        score = json.loads(game_obj.score)
        winner = max(score, key=score.get)
        for key, value in score.items():
            if value == score[winner]:
                list_of_winners.append(key)
        game_obj.is_over = 1
        game_obj.save()
        playlist_obj = Playlist.objects.filter(game=game_obj)
        song_list = []
        for row in playlist_obj:
            song_list.extend(json.loads(row.playlist).values())
        delete_message = 'Already empty!'
        workdir = 'api/static/music'
        for file in os.listdir(workdir):
            if file in song_list:
                try:
                    os.remove(f'{workdir}/{file}')
                    delete_message = 'SUCCESS'
                except Exception as e:
                    delete_message = str(e)
        return JsonResponse({'message': list_of_winners, 'delete_message': delete_message})
    except Exception as e:
        return JsonResponse({'message': str(e)})

