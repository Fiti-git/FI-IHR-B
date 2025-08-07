from django.shortcuts import render

def custom_swagger_ui(request):
    return render(request, 'swagger-ui.html')  # ✅ Correct
