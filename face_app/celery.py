from __future__ import absolute_import, unicode_literals
import os
import sys

from pathlib import Path
from celery import Celery
from django.conf import settings

BASE_DIR = Path(__file__).parent.parent.resolve()
sys.path.append(str((BASE_DIR / "detection").resolve()))
sys.path.append(str((BASE_DIR / "recognition").resolve()))

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'face_app.settings')
app = Celery('face_app')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

if __name__ == '__main__':
    app.start()