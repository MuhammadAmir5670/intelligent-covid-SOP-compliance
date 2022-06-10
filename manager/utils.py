from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

import os

def student_dir(student):
    return settings.BASE_DIR / f"media/faces_database/{student.name}-{student.roll_no}"


def profile_image_path(instance, filename):
    file_name, extension = os.path.splitext(filename)
    file_name = os.path.join(f'faces_database/{instance.name}-{instance.roll_no}', f"profile{extension}")
    return file_name


def training_image_path(instance, filename):
    student = instance.student
    student_dir = f"faces_database/{student.name}-{student.roll_no}"
    number_of_files = len(os.listdir((settings.BASE_DIR / 'media' / student_dir).resolve())) - 1

    _, extension = os.path.splitext(filename)
    return os.path.join(student_dir, f'{student.name}-{student.roll_no}-{number_of_files}{extension}')


def save_temp_image(images):
    paths = []
    temp_dir = settings.BASE_DIR / 'media/temp'
    # iterate over the image and save one by one
    for image in images:
        file_name = os.path.join(temp_dir, image.name)

        # Save file on the destination
        paths.append(default_storage.save(file_name, ContentFile(image.read())))
    
    return paths