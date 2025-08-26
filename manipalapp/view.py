from django.http import JsonResponse
from django.urls import path

def home_view(request):
    return JsonResponse({"message": "Welcome to the Healthcare API!"})
