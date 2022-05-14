from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string

from accounts.models import User
from accounts.tokens import VerificationTokenGenerator


class UserInvitationForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    token_generator = VerificationTokenGenerator
    email_template = "invitation/user-invitation.html"

    def __init__(self, request, *args, **kwargs):
        self.manager = request.user
        self.request = request
        super().__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = ['email']

    def clean_email(self):
        """ check if the email is not already registered """
        email = self.cleaned_data['email']
        # Check if the email is already registered or invited by current manager
        try:
            user = User.objects.get(email=email)
            # if the user is trying to invite himself as a moderator
            if user == self.manager:
                raise ValidationError("You can't send an invitation to yourself, try another email.")

            # if the user is already invited and has activated his account
            if user.manager == self.manager:
                if user.confirmed:
                    raise ValidationError('The user with this email is already invited and active, try another.')
                return email
            
        # if the uses is not invited
        except User.DoesNotExist:
            return email

    def get_user(self):
        email = self.cleaned_data['email']
        user, _ = User.objects.get_or_create(username=email, email=email, manager=self.manager)
        return user
    
    def save(self, commit=True):
        user = self.get_user()
        user.is_active = False
        user.set_unusable_password()
        user.confirmation_token = self.token_generator.make_token(user)

        if commit:
            user.save()
        return user

    def send(self):
        user = self.save()
        current_site = get_current_site(self.request)
        subject = "Account Invitation"
        message = render_to_string(
            self.email_template,
            {
                "admin": self.request.user,
                "user": user,
                "domain": current_site.domain,
                "uidb64": urlsafe_base64_encode(force_bytes(user.pk)),
            },
        )
        user.email_user(subject, message)