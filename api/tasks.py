import os
import subprocess

import backoff
import youtube_dl
from django.core.mail import EmailMessage, send_mail
from pytube import YouTube
from celery.decorators import task
from celery_progress.backend import ProgressRecorder
import simplejson as json


def backoff_handler(details):
    print("Backing off {wait:0.1f} seconds afters {tries} tries "
          "calling function {target} with args {args}".format(**details))


@task(name='download_and_save_music_locally', bind=True)
@backoff.on_exception(backoff.expo, Exception, max_tries=8, on_backoff=backoff_handler)
def download_and_save_music_locally(self, name, link):
    # yt = YouTube(link)
    progress_recorder = ProgressRecorder(self)
    progress_recorder.set_progress(1, 2, 'Starting Download')
    # stream = yt.streams.filter(only_audio=True).first()
    # stream.download('api/static/music/', filename=name)
    # subprocess.run(['music-dl', '--url', link, '--dir', 'api/static/music/', '--codec', 'mp3'])

    filepath = os.path.join(os.getcwd(), f'api/static/music/{name}.mp3')
    ydl_opts = {
        'outtmpl': filepath,
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])
    progress_recorder.set_progress(2, 2, 'Finished Download')


@task(name='send_code_via_email')
@backoff.on_exception(backoff.expo, Exception, max_tries=3, on_backoff=backoff_handler)
def send_code_via_email(subject, body, support, email):
    # mail = EmailMessage(subject, body, support, [email])
    # mail.send()
    send_mail(subject=subject, message=body, html_message=body, from_email=support, recipient_list=[email])
