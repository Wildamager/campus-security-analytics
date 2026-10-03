from celery import shared_task


@shared_task
def recog(ip, port, location):
    from .DetectionsNumbers import main

    main(ip, port, location)


@shared_task
def training():
    from .training_model import start

    start()