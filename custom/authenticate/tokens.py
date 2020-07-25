from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six
from .models import Account
class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        a=Account.objects.get(pk=user.id)
        return {

            six.text_type(a.id)+six.text_type(timestamp)+
            six.text_type(a.Username)
        }
account_activation_token=AccountActivationTokenGenerator()
class PasswordActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        a=Account.objects.get(pk=user.id)
        return {
            six.text_type(a.Username)+six.text_type(timestamp)+
            six.text_type(a.id)
        }
password_reset_token=PasswordActivationTokenGenerator()
