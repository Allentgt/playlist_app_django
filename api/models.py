from django.db import models
import simplejson as json

# Create your models here.


class Game(models.Model):
    """
    Game model, describes per game metadata.
    """
    name = models.CharField(max_length=300, null=False)
    sample_size = models.IntegerField(null=False)
    pool_size = models.IntegerField(null=False)
    contestants = models.IntegerField(null=False)
    ready_to_play = models.BooleanField(default=False)
    score = models.TextField(null=False, default='{}')
    all_songs = models.TextField(null=False, default='[]')
    is_over = models.BooleanField(null=False, default=False)
    game_code = models.TextField(null=False)
    
    def __str__(self):
        return self.name


class Playlist(models.Model):
    """
    Playlist model describing playlist info per contestant.
    """
    name = models.CharField(max_length=300, null=False)
    game = models.ForeignKey(Game, null=False, db_index=True, on_delete=models.CASCADE)
    playlist = models.TextField(null=False, blank=False)

    def __str__(self):
        return f"{self.name}'s Playlist"



