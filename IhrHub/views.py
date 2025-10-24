from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User, Group

def custom_swagger_ui(request):
    return render(request, 'swagger-ui.html')  # ✅ Correct


def get_user_roles(request, user_id):
    try:
        # Get the user by user_id
        user = User.objects.get(id=user_id)
        
        # Get the groups (roles) associated with the user
        user_groups = user.groups.all()
        
        # Extract the group names (roles) from the user groups
        roles = [group.name for group in user_groups]
        
        if not roles:
            return JsonResponse({'message': 'User has no roles'}, status=404)

        return JsonResponse({'user_id': user_id, 'roles': roles}, status=200)

    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)