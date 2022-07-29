from distutils.command.upload import upload
from django.db import models
from django.urls import reverse

from manager.models.student import Student
from manager.utils import screen_shot_image_path


class Violation(models.Model):
    """Model definition for Violation."""

    screen_shot = models.ImageField(upload_to=screen_shot_image_path)
    student = models.ForeignKey(Student, related_name='violations', on_delete=models.CASCADE)
    violation_time = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('students-show', kwargs={'id': self.pk})

    def image_url(self):
        return self.profile_image.url
