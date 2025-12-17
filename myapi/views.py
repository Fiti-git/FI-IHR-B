from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from rest_framework_simplejwt.tokens import RefreshToken


@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({"detail": "CSRF cookie set"})

# =========================
# JWT Helper
# =========================
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


# =========================
# SIGN UP
# =========================
@method_decorator(csrf_exempt, name="dispatch")
class SignUpView(APIView):
    """
    Register user with email & password.
    User is ACTIVE immediately.
    No email verification.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        name = request.data.get("name", "")

        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=email).exists():
            return Response(
                {"error": "User with this email already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name,
            is_active=True
        )

        return Response(
            {"message": "Registration successful. Please login."},
            status=status.HTTP_201_CREATED
        )


# =========================
# SIGN IN
# =========================
@method_decorator(csrf_exempt, name="dispatch")
class SignInView(APIView):
    """
    Login with email & password.
    Returns JWT tokens and role (if exists).
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=email, password=password)

        if not user:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        tokens = get_tokens_for_user(user)

        groups = user.groups.values_list("name", flat=True)
        role = groups[0] if groups else None

        return Response({
            "tokens": tokens,
            "user": {
                "email": user.email,
                "role": role
            }
        }, status=status.HTTP_200_OK)


# =========================
# SET ROLE
# =========================
class SetRoleView(APIView):
    """
    Set role for newly registered users.
    Can be called ONLY ONCE.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        role = request.data.get("role")

        if user.groups.exists():
            return Response(
                {"error": "Role already set"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if role not in ["Freelancer", "Job Provider"]:
            return Response(
                {"error": "Invalid role"},
                status=status.HTTP_400_BAD_REQUEST
            )

        group, _ = Group.objects.get_or_create(name=role)
        user.groups.add(group)

        return Response(
            {"message": f"Role '{role}' assigned successfully"},
            status=status.HTTP_200_OK
        )
