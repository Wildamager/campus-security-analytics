from celery import shared_task

from .DetectionsNumbers import main
from .training_model import start

@shared_task
def recog(ip, port, location):
    main(ip, port, location)

@shared_task
def training():
    start()
