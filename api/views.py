import random
from functools import reduce
from math import gcd

import simplejson as json
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from playlist.session import GAME_DETAIL
from .forms import PlaylistForm, GameForm, GameListForm, PlaylistSubmissionFormSet
from .models import Playlist, Game
from playlist import settings


def index(request):
    return render(request, 'index.html')

def terms_and_conditions(request):
    return render(request, 'tnc.html')

def about_us(request):
    return render(request, 'aboutus.html')

def feedback(request):
    return render(request, 'feedback.html')


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
            return HttpResponseRedirect('/api/put_game_details/')
    else:
        form = GameForm()

    return render(request, 'create_game.html', {'form': form})


def put_game_details(request):
    if request.method == 'POST':
        user_details = PlaylistForm(request.POST)

        if user_details.is_valid():
            user_details = user_details.cleaned_data
            error = """Sorry, I guess you have a very common name ;)"""
            username_list = [player_list.name for player_list in Playlist.objects.filter(game=user_details['game'])]
            if user_details['name'] in username_list:
                return JsonResponse({'error': error})
            pool_size = user_details['game'].pool_size
            GAME_DETAIL['name'] = user_details['name']
            GAME_DETAIL['game'] = user_details['game'].name
            GAME_DETAIL['pool_size'] = pool_size
            game_object = Game.objects.get(name=GAME_DETAIL['game'])
            playlist_object = Playlist.objects.filter(game=game_object)
            message = f'''Sorry {user_details["name"]}, You didn\'t make the cut :(\n
            May be try joining another game 
            or make better friends! '''
            if len(playlist_object) == game_object.contestants:
                return render(request, 'apology.html', {'message': message})
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
                i['link'] = i['link'].split('watch?v=')[1]
                print(i['link'])
            playlist = {i: j for i, j in zip(range(len(playlist_data)), playlist_data)}
            data = {
                'name': GAME_DETAIL['name'],
                'game': Game.objects.get(name=GAME_DETAIL['game']),
                'playlist': json.dumps(playlist)
            }
            p = Playlist(**data)
            p.save()
            game_object = Game.objects.get(name=GAME_DETAIL['game'])
            playlist_object = Playlist.objects.filter(game=game_object)
            if len(playlist_object) == game_object.contestants:
                game_object.ready_to_play = 1
                game_object.save()
            return HttpResponseRedirect('/api/thanks/')
    else:
        fs = PlaylistSubmissionFormSet(initial=[dict()] * GAME_DETAIL['pool_size'])
    context = {
        'fs': fs
    }
    request.session.clear()
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
    for i in all_random_sample:
        for j, k in i.items():
            k['name'] = j
    all_random_sample = [list(i.values())[0] for i in all_random_sample]
    return render(request, 'songs.html', {'context': all_random_sample, 'uniquePlayers': uniquePlayers, 'scorecard': scorecard})


def lcm(denominators):
    return reduce(lambda a, b: a * b // gcd(a, b), denominators)


@csrf_exempt
def vote(request):
    game = json.loads(request.POST.get('game'))
    game_obj = Game.objects.get(id=game)
    scorecard = json.loads(game_obj.score)
    votes = json.loads(request.POST.get('votes'))
    answer = request.POST.get('answer')
    max_score = lcm([i+1 for i in range(len(scorecard))])
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


@csrf_exempt
def find_duplicate_name(request):
    game = json.loads(request.POST.get('game'))
    player_name = request.POST.get('player_name')
    game_obj = Game.objects.get(id=game)
    error = """Sorry, I guess you have a very common name ;)"""
    username_list = [player_list.name for player_list in Playlist.objects.filter(game=game_obj)]
    if player_name in username_list:
        return JsonResponse({'message': error})
    else:
        return JsonResponse({'message': 'SUCCESS'})


@csrf_exempt
def game_info(request):
    game = json.loads(request.POST.get('game'))
    game_obj = Game.objects.get(id=game)
    playlist_obj = Playlist.objects.filter(game=game_obj)
    response = {
        'contestants': [player.name for player in playlist_obj],
        'available_slots': game_obj.contestants - len(playlist_obj)
    }
    return JsonResponse(response)


@csrf_exempt
def find_duplicate_game(request):
    name = request.POST.get('name')
    game_list = [game.name for game in Game.objects.all()]
    error = """Sorry, A game with the same name already exists ;)"""
    if name in game_list:
        return JsonResponse({'message': error})
    else:
        return JsonResponse({'message': 'SUCCESS'})


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
