from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings

from manager.models import Student

import shutil


@receiver(post_delete, sender=Student)
def create_student_directory(sender, instance, **kwargs):
    student_dir = settings.BASE_DIR / f'media/faces_database/{instance.name}-{instance.roll_no}'
    shutil.rmtree(student_dir)
