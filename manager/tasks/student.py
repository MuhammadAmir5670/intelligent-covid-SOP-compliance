import os
import cv2
import json

from django.core.files.uploadedfile import UploadedFile

from manager.models import Student
from manager.apps import ManagerConfig
from manager.models import Encoding
from manager.apps import ManagerConfig

from celery.decorators import task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@task(name='add_faces_to_database')
def add_faces_to_database(paths, id):
    student = Student.objects.get(pk=id)
    face_recognizer = ManagerConfig.Models['face-recognition']

    for path in paths:
        file = UploadedFile(file=open(path, 'rb'))
        image = cv2.imread(path)

        encoding = Encoding(image=file, student=student)
        locations_n_encodings = face_recognizer.get_faces(image).pop()
        encoding.face_encoding = json.dumps(locations_n_encodings[1].tolist())
        encoding.face_location = json.dumps(locations_n_encodings[0])

        encoding.save()
        file.close()
        os.remove(path)

        