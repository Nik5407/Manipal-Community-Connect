# accounts/api.py
from ninja import Router
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.http import HttpResponseRedirect, HttpRequest
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from google.oauth2 import id_token
from google.auth.transport import requests
import requests as http_requests
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.constants import ROLES, PERMISSIONS
from manipalapp.jwt import JWTAuth
from .schema import UserCreate, UserOut, UserPatch, GoogleAuthRequest, GoogleAuthResponse, RequestOtpIn, VerifyOtpIn, TokenOut, CompleteProfileIn
from .models import AuthProvider, UserProfile, ProfileType
from accounts import decorators
from service.otpservice.service import OtpService
from service.otpservice.sender import ConsoleSender

app = Router(tags=["accounts"], auth=JWTAuth())

sender = ConsoleSender() # swap with real sender in production
svc = OtpService(sender)
User = get_user_model()


@app.post("/register/", response=UserOut, auth=None)
def register_user(request, data: UserCreate):
    """
    Register a new user with their profile information.

    Args:
        request: The HTTP request object
        data (UserCreate): User registration data containing:
            - email: User's email address
            - phone_number: User's phone number
            - password: User's password
            - profile_type_id (optional): ID of the profile type
            - bio (optional): User's biography
            - phone_number (optional): User's phone number
            - date_of_birth (optional): User's date of birth

    Returns:
        UserOut: Newly created user data

    Raises:
        Http404: If the specified profile_type_id doesn't exist
    """
    user = User.objects.create_user(
        email=data.email,
        full_name=data.full_name,
        password=data.password
    )
    if data.profile_type_id:
        profile_type = get_object_or_404(ProfileType, id=data.profile_type_id)
    # else:
    #     profile_type = None

    UserProfile.objects.create(
        user=user,
        profile_type=profile_type,
        bio=data.bio,
        phone_number=data.phone_number,
        date_of_birth=data.date_of_birth 
    )
    return UserOut.model_validate(user)


@app.get("/users/", response=list[UserOut])
@decorators.permission_required(PERMISSIONS.CAN_VIEW_USER)
def list_users(request):
    """
    List all users in the system.

    Args:
        request: The HTTP request object

    Returns:
        list[UserOut]: List of all users with basic information

    Permission:
        Requires ADMIN role
    """
    return list(User.objects.values("id", "email"))


@app.get("/user/", response=UserOut)
@decorators.permission_required(PERMISSIONS.CAN_VIEW_USER)
def get_user(request):
    """
    Retrieve detailed information about a specific user.

    Args:
        request: The HTTP request object
        user_id (int): The ID of the user to retrieve

    Returns:
        UserOut: User details

    Raises:
        Http404: If user with specified ID doesn't exist

    Permission:
        Requires USER or ADMIN role
    """
    print("user value",request.user)
    return UserOut.model_validate(get_object_or_404(User, phone_number=request.user.phone_number))


@app.patch("/user/", response=UserOut)
@decorators.permission_required(PERMISSIONS.CAN_UPDATE_USER)
def patch_user(request, data: UserPatch):
    """
    Partially update authenticated user's information and profile.
    Only provided fields will be updated.

    Args:
        request: The HTTP request object
        data (UserPatch): Fields to update, all optional:
            - email: User's email address
            - phone_number: User's phone number
            - password: User's password
            - profile_type_id: ID of the profile type
            - bio: User's biography
            - phone_number: User's phone number
            - date_of_birth: User's date of birth

    Returns:
        UserOut: Updated user information

    Permission:
        Requires USER or ADMIN role
    """
    user = request.user
    user_fields = ['email', 'phone_number']
    profile_fields = ['bio', 'first_name', 'last_name', 'date_of_birth', 'gender']
    
    # Update user fields
    for field in user_fields:
        value = getattr(data, field, None)
        if value is not None:
            setattr(user, field, value)
    
    # Handle password separately since it needs special treatment
    if data.password is not None:
        user.set_password(data.password)
    
    user.save()

    # Update profile fields
    if hasattr(user, "profile"):
        profile = user.profile
        for field in profile_fields:
            value = getattr(data, field, None)
            if value is not None:
                setattr(profile, field, value)
        profile.save()

    return UserOut.model_validate(user)


@app.delete("/user/")
@decorators.permission_required(PERMISSIONS.CAN_DELETE_USER)
def delete_user(request):
    """
    Delete authenticated user and their associated profile.

    Args:
        request: The HTTP request object

    Returns:
        dict: Success message confirming deletion

    Permission:
        Requires USER or ADMIN role
    """
    user = request.user
    user.is_deleted = True
    user.save()
    return {"success": True, "message": "User deleted successfully"}


@app.get("/google/login/", auth=None)
def google_login(request):
    """
    Initiates the Google OAuth2 login flow by redirecting to Google's consent page.
    """
    oauth2_params = {
        'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
        'redirect_uri': settings.GOOGLE_OAUTH2_REDIRECT_URI,
        'scope': 'email profile',
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'consent',
    }
    
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{'&'.join(f'{k}={v}' for k, v in oauth2_params.items())}"
    return HttpResponseRedirect(auth_url)


@app.get("/google/callback/", response=GoogleAuthResponse, auth=None)
def google_callback(request, code: str = None, error: str = None):
    """
    Handles the Google OAuth2 callback and creates/authenticates the user.
    """
    if error:
        return {"error": error}

    if not code:
        return {"error": "Authorization code is missing"}

    # Exchange code for tokens
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
        "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_OAUTH2_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    response = http_requests.post(token_url, data=token_data)
    if not response.ok:
        return {"error": "Failed to get access token"}

    tokens = response.json()

    # Verify ID token
    try:
        id_info = id_token.verify_oauth2_token(
            tokens["id_token"],
            requests.Request(),
            settings.GOOGLE_OAUTH2_CLIENT_ID,
        )
    except ValueError:
        return {"error": "Invalid ID token"}

    # Check if email exists and is verified
    email = id_info["email"]
    try:
        user = User.objects.get(email=email)
        if not user.is_email_verified:
            return {"error": "Please verify your email through phone login first"}
            
        # Update auth provider to include Google
        user.auth_provider = AuthProvider.GOOGLE
        user.save(update_fields=["auth_provider"])
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        return GoogleAuthResponse(
            access_token=str(refresh.access_token),
            refresh_token=str(refresh),
            user=UserOut.model_validate(user)
        )
    except User.DoesNotExist:
        return {"error": "Please login with phone number first and verify your email"}

# OTP API


@app.post("/request-otp", auth=None)
def request_otp(request: HttpRequest, payload: RequestOtpIn):
    try:
        svc.request_otp(payload.identifier, payload.channel)
        return {"ok": True, "message": "OTP sent"}
    except ValueError as e:
        request.status_code = 400
        return {"ok": False, "error": str(e)}


@app.post("/verify-otp", auth=None)
def verify_otp(request, payload: VerifyOtpIn):
    try:
        # Validate if identifier is email
        try:
            validate_email(payload.identifier)
            is_email = True
        except ValidationError:
            is_email = False
            
        result = svc.verify_otp(payload.identifier, payload.code, is_email_verification=is_email)
        return result
    except ValueError as e:
        request.status_code = 400
        return {"error": str(e)}


@app.post("/complete-profile", response=TokenOut, auth=None)
def complete_profile(request, payload: CompleteProfileIn):
    try:
        profile_data = {
            "first_name": payload.first_name,
            "last_name": payload.last_name,
            "email": payload.email,
            "date_of_birth": payload.date_of_birth,
            "gender": payload.gender,
            "is_referred": payload.is_referred
        }

        if payload.verification_id:
            # OTP flow
            tokens = svc.complete_profile(
                verification_id=payload.verification_id,
                profile_data=profile_data
            )
        else:
            raise ValueError("erifVication_id is required")

        return tokens
    except ValueError as e:
        request.status_code = 400
        return {"error": str(e)}