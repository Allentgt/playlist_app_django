from django.db import models


# Create your models here.


class Game(models.Model):
    """
    Game model, describes per game metadata.
    """
    name = models.CharField(max_length=300, null=False)
    sample_size = models.IntegerField(null=False)
    contestants = models.IntegerField(null=False)


class Playlist(models.Model):
    """
    Playlist model describing playlist info per contestant.
    """
    name = models.CharField(max_length=300, null=False)
    game = models.ForeignKey(Game, null=False, db_index=True, on_delete=models.CASCADE)
    playlist = models.TextField(null=False, blank=False)


