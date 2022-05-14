from django.contrib.auth.tokens import PasswordResetTokenGenerator

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    pass


VerificationTokenGenerator = AccountActivationTokenGenerator()