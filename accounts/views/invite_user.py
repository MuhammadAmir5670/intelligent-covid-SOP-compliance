from django.shortcuts import render, redirect
from django.views.generic import View

from accounts.forms import UserInvitationForm
from accounts.tokens import VerificationTokenGenerator


class InviteUser(View):
    form = UserInvitationForm
    template_name = 'invitation/invite-user.html'
    token_generator = VerificationTokenGenerator

    def get(self, request):
        self.request = request
        form = self.form(request)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        self.request = request
        form = self.form(request=request, data=request.POST)
        if form.is_valid():
            form.send()
            return redirect('index')
        
        return render(request, self.template_name, {'form': form})