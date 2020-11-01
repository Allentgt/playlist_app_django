import time
from pytube import YouTube
from celery.decorators import task


@task(name='sleep_for_10')
def sleep_for_10():
    time.sleep(10)


@task(name='download_and_save_music_locally')
def download_and_save_music_locally(name, link):
    yt = YouTube(link)
    stream = yt.streams.filter(only_audio=True).first()
    stream.download(f'api/static/music/', filename=name)
