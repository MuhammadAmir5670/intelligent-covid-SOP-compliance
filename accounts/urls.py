from django.urls import path, include
from django.contrib.auth import urls as auth_urls
from django.contrib.auth.views import LoginView
from accounts.views import SignupView, InviteUser, AcceptInvite

urlpatterns = [
    path('login/', LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('register/', SignupView.as_view(), name='registration'),
    path('invite/new', InviteUser.as_view(), name='invite-user'),
    path("accept/<uidb64>/<token>/", AcceptInvite.as_view(), name="accept-invitation"),
    path('', include(auth_urls)),
]