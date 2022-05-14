from django.shortcuts import render, redirect
from django.views.generic import View
from accounts.models import User

from accounts.forms import ManagerForm

class SignupView(View):
    template_name = 'registration/signup.html'
    form = ManagerForm

    def get(self, request):
        form = self.form()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = self.form(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login')
        
        return render(request, self.template_name, {'form': form})
