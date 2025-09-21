from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
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
    View to handle user registration (sign-up) with email and password.
    """
    def post(self, request):
        data = request.data
        email = data.get('email')
        password = data.get('password')
        name = data.get('name', '')

        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=400)

        # Check if the email is already in use
        if User.objects.filter(username=email).exists():
            return Response({'error': 'User already exists'}, status=400)

        # Create the new user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name
        )

        # Generate JWT tokens
        tokens = get_tokens_for_user(user)

        return Response({'message': 'User created', 'tokens': tokens}, status=201)

class SignInView(APIView):
    """
    View to handle user login (sign-in) with email and password.
    """
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=400)

        # Authenticate the user
        user = authenticate(username=email, password=password)
        
        if user:
            # Generate JWT tokens
            tokens = get_tokens_for_user(user)
            return Response({'tokens': tokens})
        else:
            return Response({'error': 'Invalid credentials'}, status=401)

class GoogleLoginView(APIView):
    """
    View to handle Google OAuth login using an ID token.
    """
    def post(self, request):
        token = request.data.get("token")
        
        if not token:
            return Response({"error": "Token not provided"}, status=400)

        try:
            # Replace with your actual Google CLIENT_ID
            CLIENT_ID = "858134682989-mav50sd3csolb7u8tbc1susrhm5uvk49.apps.googleusercontent.com"
            
            # Verify the Google ID token
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), CLIENT_ID)

            email = idinfo["email"]
            name = idinfo.get("name", "")

            # Get or create the user
            user, created = User.objects.get_or_create(username=email, defaults={
                "email": email,
                "first_name": name,
            })

            # Generate JWT tokens
            tokens = get_tokens_for_user(user)

            return Response({'tokens': tokens})

        except ValueError:
            return Response({"error": "Invalid token"}, status=401)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


def google_oauth_callback(request):
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"error": "Missing code"}, status=400)

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": "http://localhost:8000/api/google-oauth-callback/",
        "grant_type": "authorization_code",
    }

    token_res = requests.post(token_url, data=data)
    token_data = token_res.json()

    if "error" in token_data:
        return JsonResponse({"error": token_data.get("error_description")}, status=400)

    id_token = token_data.get("id_token")
    access_token = token_data.get("access_token")

    # Optionally decode and verify ID token to get user info
    userinfo_res = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    userinfo = userinfo_res.json()

    # Here you’d create or log in the user in Django
    # Example:
    # user = get_or_create_user(userinfo["email"], userinfo["name"], ...)

    return JsonResponse({
        "id_token": id_token,
        "access_token": access_token,
        "user": userinfo
    })

def linkedin_oauth_callback(request):
    code = request.GET.get('code')
    if not code:
        return JsonResponse({"error": "Missing authorization code"}, status=400)

    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': settings.LINKEDIN_REDIRECT_URI,
        'client_id': settings.LINKEDIN_CLIENT_ID,
        'client_secret': settings.LINKEDIN_CLIENT_SECRET,
    }

    token_response = requests.post(token_url, data=data)
    token_json = token_response.json()

    access_token = token_json.get('access_token')
    id_token = token_json.get('id_token')

    if not access_token or not id_token:
        return JsonResponse({"error": "Failed to get tokens"}, status=400)

    # Decode id_token to get user info (don't skip validation in production)
    try:
        decoded = jwt.decode(id_token, options={"verify_signature": False})  # TODO: verify signature with JWKS
        email = decoded.get('email')
        first_name = decoded.get('given_name', '')
        last_name = decoded.get('family_name', '')
        full_name = decoded.get('name', '').strip()
    except Exception as e:
        return JsonResponse({"error": f"Failed to decode ID token: {str(e)}"}, status=400)

    if not email:
        return JsonResponse({"error": "Email not provided in ID token"}, status=400)

    # Create or get user
    user, created = User.objects.get_or_create(username=email, defaults={
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
    })

    tokens = get_tokens_for_user(user)

    return JsonResponse({
        'tokens': tokens,
        'user': {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'full_name': full_name,
        }
    })
#     return HttpResponseRedirect(f"/welcome?token={access_token}")