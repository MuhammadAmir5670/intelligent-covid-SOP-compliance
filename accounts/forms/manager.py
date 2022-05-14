from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from accounts.models import User


class ManagerForm(UserCreationForm):

    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        """ check if the email is not already registered """
        email = self.cleaned_data['email']
        try:
            User.objects.get(email=email, role=User.Roles.manager)
            raise ValidationError('This email is already registered, try another.')
        except User.DoesNotExist:
            return email

    def save(self):
        user = super().save(commit=False)
        user.role = User.Roles.manager
        user = user.save()
        return user
