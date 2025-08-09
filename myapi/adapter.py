# myapi/adapter.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin
from dj_rest_auth.views import LoginView
from dj_rest_auth.registration.views import SocialLoginView
from django.http import HttpRequest

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    This adapter is used to hook into the allauth social login process.
    """

    def pre_social_login(self, request: HttpRequest, sociallogin: SocialLogin):
        """
        This method is called just before the social login is processed.
        We can use this hook to perform custom actions. For our purpose,
        we check if a user with this email already exists. If so, we connect
        the social account to the existing user.
        """
        # sociallogin.user is the new user created by allauth
        # sociallogin.account is the social account
        
        # Check if a user with this email already exists.
        if sociallogin.user.id:
            return

        try:
            user = self.get_user_model().objects.get(email=sociallogin.user.email)
            # If the user exists, connect the social account to this user
            sociallogin.connect(request, user)
        except self.get_user_model().DoesNotExist:
            # If the user does not exist, let allauth create a new one
            pass

    def get_user_model(self):
        # Helper to get the user model configured in settings
        from django.contrib.auth import get_user_model
        return get_user_model()