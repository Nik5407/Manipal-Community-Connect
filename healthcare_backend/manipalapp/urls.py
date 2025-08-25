"""
URL configuration for manipalapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from ninja import NinjaAPI
from manipalapp.api import api

from .view import home_view
from accounts.token_view import jwt_urlpatterns
from accounts.views import login_view


# Add router 
# api.add_router("/accounts/", api)

urlpatterns = [
    path("", home_view),
    path("login/", login_view, name="login"),
    path("admin/", admin.site.urls),
    path("api/v1/", api.urls),# Ninja API
    path("api/v1/auth/", include(jwt_urlpatterns)),  # DRF JWT views
    # path("api/v1/accounts/", include("accounts.urls")),  # Accounts API including Google auth
    # path("api/v1/services/", include("services.urls")),  # Services API including OTP
]
