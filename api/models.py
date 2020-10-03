from django.db import models


# Create your models here.

class Playlist(models.Model):
    """
    Model :
    Viewset :
    Serializers :
    Router :
    Description :
    """
    name = models.CharField(max_length=300, null=True)
    playlist = models.TextField(null=False, blank=True)
