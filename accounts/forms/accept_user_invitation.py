from django.contrib.auth.forms import UserCreationForm

from accounts.models import User

class AcceptInvitationForm(UserCreationForm):
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = True
        user.confirmed = True
        user.token = None
        if commit:
            user.save()
        return user
