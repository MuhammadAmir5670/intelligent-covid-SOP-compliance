from django.db import models

from manager.utils import image_path


class Student(models.Model):
    name = models.CharField(max_length=255)
    roll_no =  models.IntegerField(unique=True)
    email = models.EmailField(unique=True)
    profile_image = models.ImageField(upload_to=image_path)

    def __str__(self):
        return self.name

    def image_url(self):
        return self.profile_image.url

    class Meta:
        ordering = ['roll_no']