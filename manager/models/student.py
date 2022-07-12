from django.db import models
from django.urls import reverse

from manager.utils import profile_image_path


class Student(models.Model):
    name = models.CharField(max_length=255)
    roll_no =  models.IntegerField(unique=True)
    email = models.EmailField(unique=True)
    profile_image = models.ImageField(upload_to=profile_image_path)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('students-show', kwargs={'id': self.pk})

    def image_url(self):
        return self.profile_image.url

    class Meta:
        ordering = ['roll_no']