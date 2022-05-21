from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

import os

def image_path(instance, filename):
    file_name, extension = os.path.splitext(filename)
    file_name = os.path.join(f'faces_database/{instance.name}-{instance.roll_no}', f'profile{extension}')
    print(file_name)
    return file_name


def save_to_faces_database(images, student):
    student_dir = os.path.join(settings.BASE_DIR  / f'media/faces_database/{student.name}-{student.roll_no}')
    
    # Create root directory for student if it does not exists
    if not os.path.isdir(student_dir):
        os.makedirs(student_dir)

    # iterate over the image and save one by one 
    for counter, image in enumerate(images):
        file_name, extension = os.path.splitext(image.name)
        file_name = os.path.join(student_dir, f'{student.name}-{counter}{extension}')

        # Save file on the destination
        default_storage.save(file_name, ContentFile(image.read()))