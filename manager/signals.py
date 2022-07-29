from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.conf import settings

from manager.models import Student

import os
import shutil

from manager.models.violation import Violation


@receiver(post_delete, sender=Student)
def create_student_directory(sender, instance, **kwargs):
    student_dir = settings.BASE_DIR / f'media/faces_database/{instance.name}-{instance.roll_no}'
    shutil.rmtree(student_dir)

@receiver(pre_save, sender=Student)
def update_student_directory(sender, instance, **kwargs):
    student_dir = settings.BASE_DIR / f'media/faces_database/{instance.name}-{instance.roll_no}'
    
    if instance.id and os.path.isdir(student_dir): 
        student = Student.objects.get(pk=instance.id)
        source = settings.BASE_DIR / f'media/faces_database/{student.name}-{student.roll_no}'

        os.rename(source, student_dir)
    else:
        os.makedirs(student_dir)

@receiver(post_delete, sender=Violation)
def create_student_directory(sender, instance, **kwargs):
    os.remove(instance.screen_shot.path)