import os
import json

from django.db import models

from manager.models import Student
from manager.utils import training_image_path

decoder = json.decoder.JSONDecoder()

class Encoding(models.Model):
    """Model definition for Encoding."""

    image = models.ImageField(upload_to=training_image_path)
    active = models.BooleanField(default=True)
    face_location = models.TextField()
    face_encoding = models.TextField()
    student = models.ForeignKey(to=Student, on_delete=models.CASCADE, related_name="encodings")
    
    def location(self):
        """returns the decoded version of the face_location textfield"""
        return decoder.decode(self.face_location)
    
    def encoding(self):
        """returns the decoded version of the face_encoding textfield"""
        return decoder.decode(self.face_encoding)

    def __str__(self):
        """Unicode representation of Encoding."""
        return f'Encoding: {os.path.basename(self.image.name)}'
