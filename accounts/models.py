from audioop import reverse
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Model definition for Admin."""

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Roles(models.TextChoices):
        manager = 1, "Manager"
        moderator = 2, "Moderator"

    # TODO: Define fields here
    role = models.PositiveSmallIntegerField(choices=Roles.choices, editable=False, null=True)
    manager = models.ForeignKey(
        "self",
        related_name="moderators",
        on_delete=models.CASCADE,
        editable=False,
        default=None,
        null=True,
    )

    # Email Confirmation and Invitaion fields
    confirmation_token = models.CharField(max_length=40, editable=False, default=None, null=True)
    confirmed = models.BooleanField(editable=False, default=False)

    def is_manager(self):
        return self.role == int(self.Roles.manager.value)

    def is_supervisor(self):
        return self.role == int(self.Roles.moderator.value)

    def __str__(self):
        """Unicode representation of Admin."""
        return f"{self.email}"
