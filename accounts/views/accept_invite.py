from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic import View
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib import messages
from django.core.exceptions import ValidationError

from accounts.forms import AcceptInvitationForm
from accounts.models import User
from accounts.tokens import VerificationTokenGenerator


class AcceptInvite(View):
    template_name = 'invitation/accept-invitation.html'
    form = AcceptInvitationForm
    token_generator = VerificationTokenGenerator


    def get(self, request, uidb64, token):
        """
        If the link is valid displays the form to prompt additional user 
        information to complete the account activation process
        """
        self.validlink = False
        self.user = self.get_user(uidb64=uidb64)

        if self.user and self.validate_token(token):
            self.validlink = True
        
        return render(request, self.template_name, self.get_context_data())


    def post(self, request, uidb64, token):
        """
        activates the account with the given information and redirect 
        to the login page if the user account is successfully activated
        """
        self.user = self.get_user(uidb64)
        
        if self.user and self.validate_token(token):
            form = self.form(request.POST, instance=self.user)
            if form.is_valid():
                form.save()
                messages.success(request, "Your account has been created and activated successfully")
                return redirect("login")
        else:
            raise Http404

        return render(request, self.template_name, {'form': form})

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
            user = None
        return user

    def validate_token(self, token):
        print(self.user.confirmation_token)
        if self.user.confirmation_token == token and self.token_generator.check_token(self.user, token):
            return True
        return False
    
    def get_context_data(self, **kwargs):
        context = {}
        context['validlink'] = self.validlink
        context['form'] = self.form()
        context.update(kwargs)
        return context
