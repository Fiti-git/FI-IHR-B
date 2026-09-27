from django.contrib.auth.models import User, Group,Permission
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.utils.timesince import timesince


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


class AdminUserPermissionsAPIView(APIView):
    """
    Admin API to get all users with their groups and permissions
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.all().prefetch_related(
            "groups",
            "user_permissions"
        )

        data = []

        for user in users:
            group_permissions = Permission.objects.filter(
                group__user=user
            ).distinct()

            all_permissions = set(
                list(user.user_permissions.all()) +
                list(group_permissions)
            )

            data.append({
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "is_active": user.is_active,
                "is_staff": user.is_staff,
                "groups": [g.name for g in user.groups.all()],
                "permissions": [
                    {
                        "id": p.id,
                        "codename": p.codename,
                        "name": p.name,
                        "app": p.content_type.app_label
                    }
                    for p in all_permissions
                ]
            })

        return Response(data)

class MyPermissionsAPIView(APIView):
    """
    Returns permissions of the logged-in user only
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Direct permissions
        user_permissions = user.user_permissions.all()

        # Group permissions
        group_permissions = Permission.objects.filter(
            group__user=user
        ).distinct()

        all_permissions = set(user_permissions) | set(group_permissions)

        data = {
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "is_staff": user.is_staff,
                "groups": list(user.groups.values_list("name", flat=True)),
            },
            "permissions": [
                {
                    "id": perm.id,
                    "codename": perm.codename,
                    "name": perm.name,
                    "app": perm.content_type.app_label,
                }
                for perm in all_permissions
            ],
        }

        return Response(data)
    
class RecentAdminActionsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Filter actions only for logged-in user
        queryset = LogEntry.objects.filter(user=request.user).order_by('-action_time')[:20]

        actions = []
        for entry in queryset:
            if entry.action_flag == ADDITION:
                action_type = "Added"
            elif entry.action_flag == CHANGE:
                action_type = "Changed"
            elif entry.action_flag == DELETION:
                action_type = "Deleted"
            else:
                action_type = "Action"

            object_repr = entry.object_repr or "Object"
            time_ago = timesince(entry.action_time) + " ago"
            description = f"{action_type} {object_repr}."

            if entry.change_message and entry.change_message != "{}":
                description += f" {entry.change_message}"

            actions.append({
                "id": entry.id,
                "time_ago": time_ago,
                "object": object_repr,
                "description": description,
                "user": entry.user.username,
            })

        return Response(actions)
    
class LoggedInUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        data = {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        }

        return Response(data)
    
