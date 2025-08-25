from django.urls import path, include
from .token_view import jwt_urlpatterns

urlpatterns = [
    path("auth/", include(jwt_urlpatterns)),  # Handles token/, refresh/, verify/
]
