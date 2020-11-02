from pytube import YouTube
from celery.decorators import task
from celery_progress.backend import ProgressRecorder
from retrying import retry


@task(name='download_and_save_music_locally', bind=True)
@retry(stop_max_attempt_number=5)
def download_and_save_music_locally(self, name, link):
    yt = YouTube(link)
    progress_recorder = ProgressRecorder(self)
    progress_recorder.set_progress(1, 2, 'Starting Download')
    stream = yt.streams.filter(only_audio=True).first()
    stream.download(f'api/static/music/', filename=name)
    progress_recorder.set_progress(1, 2, 'Finished Download')

