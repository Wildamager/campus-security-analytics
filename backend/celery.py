import os
from datetime import timedelta

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

app = Celery("backend")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

# app.conf.beat_schedule = {
#     "mul": {
#         "task": "mul",
#         # 'schedule': crontab(minute=1),
#         "schedule": timedelta(seconds=10),
#         "args": (2, 3),
#     }
# }



