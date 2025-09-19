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
from django.views.generic import RedirectView

class EmailVerificationRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        # Customize this URL to your frontend's success page
        return "http://127.0.0.1:8000/email-verified-successfully"

# The existing ProtectedView from the previous guide
class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {'message': f'Hello, {request.user.email}! You are seeing a protected view.'}
        return Response(content)


# THIS IS THE NEW VIEW
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    # callback_url = "http://127.0.0.1:8000/api/auth/google/"
    client_class = OAuth2Client
    callback_url = "http://localhost:3000"
    

    # ADD THIS METHOD TO DEBUG
    def post(self, request, *args, **kwargs):
        # --- START DIAGNOSTIC ---
        from allauth.socialaccount.models import SocialApp
        from django.contrib.sites.models import Site

        print("--- Inside GoogleLogin View ---")
        try:
            # Check what SITE_ID Django is currently using
            current_site = Site.objects.get_current()
            print(f"Current Site from get_current(): {current_site.name} (ID: {current_site.id})")

            # Try to fetch the SocialApp exactly how allauth would
            app = SocialApp.objects.get(provider='google', sites=current_site)
            print(f"Successfully fetched SocialApp: {app.name}")
            print(f"   - Client ID starts with: {app.client_id[:5]}...")
            print(f"   - Linked to sites: {[site.name for site in app.sites.all()]}")

        except Site.DoesNotExist:
            print("ERROR: Could not find a current Site. Is SITE_ID correct?")
        except SocialApp.DoesNotExist:
            print("ERROR: SocialApp.objects.get query FAILED. This is the root cause.")
            print("       - Provider being queried: 'google'")
            print(f"      - Site being queried: {current_site.name}")

        print("--- End Diagnostic ---")
        
        # Continue with the normal login process
        return super().post(request, *args, **kwargs)

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