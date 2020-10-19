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
]
