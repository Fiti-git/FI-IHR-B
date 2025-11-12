from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from .utils import account_activation_token



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import requests
from django.http import JsonResponse, HttpResponseRedirect
from django.conf import settings
import jwt


def get_tokens_for_user(user):
    """
    Helper function to generate JWT tokens for the authenticated user.
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class SignUpView(APIView):
    """
    Handles new user registration.
    Creates an inactive user and sends a verification email.
    Does NOT return login tokens.
    """
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        name = request.data.get('name', '')

        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=email).exists():
            return Response({'error': 'A user with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the user but as inactive
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name
        )
        
        ## CHANGE: Set the user to inactive until they verify their email.
        user.is_active = False
        user.save()

        ## CHANGE: Send the verification email.
        send_verification_email(user, request) # Assumes this function is in your myapi/views.py or myapi/utils.py

        ## CHANGE: Do NOT generate or return tokens.
        ## Instead, return a success message instructing the user to check their email.
        return Response(
            {"message": "Registration successful. Please check your email to verify your account."},
            status=status.HTTP_201_CREATED
        )

#====================================================================
# 2. Refactored SignInView
#====================================================================
class SignInView(APIView):
    """
    Handles user login.
    Checks if the user is active (verified) and returns their role.
    """
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=email, password=password)
        
        if user:
            ## CHANGE: Check if the user has verified their email.
            if not user.is_active:
                return Response({'error': 'Please verify your email before logging in.'}, status=status.HTTP_403_FORBIDDEN)
            
            tokens = get_tokens_for_user(user)
            
            ## CHANGE: Get the user's role from their group assignment.
            user_groups = user.groups.values_list('name', flat=True)
            role = user_groups[0] if user_groups else None # e.g., 'job provider' or null

            ## CHANGE: Return the user's role along with the tokens.
            return Response({
                'tokens': tokens,
                'user': {'role': role}
            })
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

#====================================================================
# 3. Refactored GoogleLoginView
#====================================================================
class GoogleLoginView(APIView):
    """
    Handles Google OAuth login.
    Email is considered pre-verified by Google. The user is set to active.
    Returns the user's role so the frontend can decide to redirect to the dashboard or to role selection.
    """
    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"error": "Token not provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            CLIENT_ID = "858134682989-mav50sd3csolb7u8tbc1susrhm5uvk49.apps.googleusercontent.com"
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), CLIENT_ID)
            email = idinfo["email"]
            name = idinfo.get("name", "")

            ## CHANGE: Use get_or_create and ensure the user is active.
            user, created = User.objects.get_or_create(username=email, defaults={
                "email": email,
                "first_name": name,
                "is_active": True, # Social login emails are considered verified.
            })
            
            # If an existing user was inactive, activate them.
            if not created and not user.is_active:
                user.is_active = True
                user.save()

            tokens = get_tokens_for_user(user)

            ## CHANGE: Get and return the user's role, same as in SignInView.
            user_groups = user.groups.values_list('name', flat=True)
            role = user_groups[0].lower() if user_groups else None

            return Response({
                'tokens': tokens,
                'user': {'role': role}
            })
        except ValueError:
            return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#====================================================================
# 4. Refactored LinkedIn Callback
# NOTE: This should be a DRF APIView for consistency.
#====================================================================
class LinkedInLoginView(APIView):
    """
    Handles the LinkedIn OAuth callback.
    Similar logic to Google: creates an active user and returns their role.
    """
    def post(self, request):
        code = request.data.get('code')
        if not code:
            return Response({"error": "Missing authorization code"}, status=status.HTTP_400_BAD_REQUEST)

        # Step 1: Exchange code for access token
        token_response = requests.post("https://www.linkedin.com/oauth/v2/accessToken", data={
            'grant_type': 'authorization_code', 'code': code,
            'redirect_uri': settings.LINKEDIN_REDIRECT_URI,
            'client_id': settings.LINKEDIN_CLIENT_ID,
            'client_secret': settings.LINKEDIN_CLIENT_SECRET,
        })
        token_data = token_response.json()
        access_token = token_data.get('access_token')

        if not access_token:
            return Response({"error": "Failed to retrieve access token from LinkedIn"}, status=status.HTTP_400_BAD_REQUEST)

        # Step 2: Use access token to get user's profile info (including email)
        profile_response = requests.get("https://api.linkedin.com/v2/userinfo", headers={
            "Authorization": f"Bearer {access_token}"
        })
        profile_data = profile_response.json()
        email = profile_data.get('email')
        
        if not email:
            return Response({"error": "Could not retrieve email from LinkedIn"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Step 3: Get or create the user in your database
        user, created = User.objects.get_or_create(username=email, defaults={
            'email': email,
            'first_name': profile_data.get('given_name', ''),
            'last_name': profile_data.get('family_name', ''),
            'is_active': True,
        })

        if not created and not user.is_active:
            user.is_active = True
            user.save()

        # Step 4: Generate tokens and return role
        tokens = get_tokens_for_user(user)
        user_groups = user.groups.values_list('name', flat=True)
        role = user_groups[0].lower() if user_groups else None

        return Response({
            'tokens': tokens,
            'user': {'role': role}
        })

def send_verification_email(user, request):
    """
    Sends the verification email using the configured Django email backend,
    which is now Anymail + Mailgun.
    """
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    
    # Construct the verification link that points to your BACKEND API
    # The frontend will handle the final redirect after a successful API call.
    verification_url = f"http://206.189.134.117:8000/myapi/verify-email/{uid}/{token}/"
    
    subject = "Verify your email for IHRHUB"
    
    # Simple text-based email body
    message = f"""
Hi {user.username},

Thank you for registering with IHRHUB!

Please click the link below to verify your email and activate your account:
{verification_url}

If you did not sign up for an account, you can safely ignore this email.

Thanks,
The HRHUB Team
"""
    # This send_mail function now sends through Mailgun automatically!
    # It uses the DEFAULT_FROM_EMAIL from settings.py
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL, # from_email
        [user.email],               # recipient_list
        fail_silently=False,
    )

class VerifyEmailView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            # SUCCESS: Redirect to the frontend login page with a success flag
            frontend_url = 'http://206.189.134.117/login?verified=true'
            return HttpResponseRedirect(frontend_url)
        else:
            # FAILURE: Redirect to a frontend error page or the register page
            frontend_url = 'http://206.189.134.117/register?error=invalid_link'
            return HttpResponseRedirect(frontend_url)


# --- 2. ROLE SELECTION ---

class SetRoleView(APIView):
    """
    A protected view for a newly verified user to set their role.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        role_name = request.data.get("role") # Expects "Freelancer" or "Job Provider"

        # Prevent users from changing their role
        if user.groups.exists():
            return Response({"error": "Role has already been set and cannot be changed."}, status=status.HTTP_400_BAD_REQUEST)

        if role_name not in ["Freelancer", "Job Provider"]:
            return Response({"error": "Invalid role specified."}, status=status.HTTP_400_BAD_REQUEST)

        # Capitalize to match the Group name
        group_name = role_name.capitalize()
        try:
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
            return Response({"message": f"Role successfully set as {group_name}."}, status=status.HTTP_200_OK)
        except Group.DoesNotExist:
            return Response({"error": f"The '{group_name}' role does not exist on the server."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
