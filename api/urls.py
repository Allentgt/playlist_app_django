from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('thanks/', views.thanks, name='thanks'),
    path('randomise/<str:game>/', views.randomise, name='randomise'),
    path('put_playlist/', views.put_playlist, name='put_playlist'),
    path('create_game/', views.create_game, name='create_game'),
    path('get_games/', views.get_games, name='get_games'),
    path('put_game_details/', views.put_game_details, name='put_game_details'),
    path('vote/', views.vote, name='vote'),
    path('find_duplicate_name/', views.find_duplicate_name, name='find_duplicate_name'),
    path('find_duplicate_game/', views.find_duplicate_game, name='find_duplicate_game'),
    path('game_info/', views.game_info, name='game_info'),
    path('send_support_mail/', views.send_support_mail, name='send_support_mail'),
]
