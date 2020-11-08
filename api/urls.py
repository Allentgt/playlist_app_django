from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('thanks/', views.thanks, name='thanks'),
    path('randomise/<str:game>/', views.randomise, name='randomise'),
    path('put_playlist/', views.put_playlist, name='put_playlist'),
    path('poll_download/', views.poll_download, name='poll_download'),
    path('create_game/', views.create_game, name='create_game'),
    path('get_games/', views.get_games, name='get_games'),
    path('vote/', views.vote, name='vote'),
    path('game_info/', views.game_info, name='game_info'),
    path('game_data/', views.game_data, name='game_data'),
    path('send_support_mail/', views.send_support_mail, name='send_support_mail'),
    path('tnc/', views.terms_and_conditions, name='terms_and_conditions'),
    path('about_us/', views.about_us, name='about_us'),
    path('feedback/', views.feedback, name='feedback'),
    path('gameinfo/', views.game_info_howto, name='game_info_howto'),
    path('end_game/', views.end_game, name='end_game'),
    path('new_game/', views.new_game, name='new_game'),
    path('new_entry/', views.new_entry, name='new_entry'),
    path('play_games/', views.play_games, name='play_games'),
]
