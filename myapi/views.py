# myapi/views.py

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt.tokens import RefreshToken

# The existing ProtectedView from the previous guide
class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {'message': f'Hello, {request.user.email}! You are seeing a protected view.'}
        return Response(content)


# THIS IS THE NEW VIEW
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    # In a real-world app, you'd probably want to set this from settings
    callback_url = "http://127.0.0.1:8000/api/auth/google/"
    client_class = OAuth2Client

@login_required
def auth_success(request):
    """
    A view that the user is redirected to after a successful login.
    It generates JWTs and passes them to the template.
    """
    # The user is available at request.user
    user = request.user

    # Generate JWT tokens for the user
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    # Prepare the context to pass to the template
    context = {
        'user': user,
        'access_token': access_token,
        'refresh_token': refresh_token,
    }

    # Render the success page template
    return render(request, 'auth_success.html', context)

def login_page(request):
    """
    A simple page that provides a link to log in with Google.
    """
    return render(request, 'login_page.html')