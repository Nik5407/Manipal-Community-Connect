# accounts/api.py
from ninja import Router
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from accounts.constants import ROLES
from manipalapp.jwt import JWTAuth
from .schema import UserCreate, UserOut
from .models import UserProfile, ProfileType
from accounts import decorators

app = Router(tags=["accounts"], auth=JWTAuth())
User = get_user_model()


@app.post("/register/", response=UserOut)
def register_user(request, data: UserCreate):
    """
    Register a new user with their profile information.

    Args:
        request: The HTTP request object
        data (UserCreate): User registration data containing:
            - email: User's email address
            - full_name: User's full name
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
    else:
        profile_type = None

    UserProfile.objects.create(
        user=user,
        profile_type=profile_type,
        bio=data.bio,
        phone_number=data.phone_number,
        date_of_birth=data.date_of_birth 
    )
    return UserOut.model_validate(user)


@app.get("/users/", response=list[UserOut])
@decorators.role_required([ROLES.ADMIN])
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
    return list(User.objects.values("id", "email", "full_name"))


@app.get("/users/{user_id}", response=UserOut)
@decorators.role_required([ROLES.USER, ROLES.ADMIN])
def get_user(request, user_id: int):
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
    return UserOut.model_validate(get_object_or_404(User, id=user_id))


@app.put("/users/{user_id}", response=UserOut)
@decorators.role_required([ROLES.USER, ROLES.ADMIN])
def update_user(request, user_id: int, data: UserCreate):
    """
    Update user information and their profile.

    Args:
        request: The HTTP request object
        user_id (int): The ID of the user to update
        data (UserCreate): Updated user data containing:
            - email: User's email address
            - full_name: User's full name
            - password (optional): User's new password
            - profile_type_id (optional): ID of the profile type
            - bio (optional): User's biography
            - phone_number (optional): User's phone number
            - date_of_birth (optional): User's date of birth

    Returns:
        UserOut: Updated user information

    Raises:
        Http404: If user with specified ID doesn't exist

    Permission:
        Requires USER or ADMIN role
    """
    user = get_object_or_404(User, id=user_id)
    user.email = data.email
    user.full_name = data.full_name
    if data.password:
        user.set_password(data.password)
    user.save()

    if hasattr(user, "profile"):
        profile = user.profile
        profile.profile_type_id = data.profile_type_id
        profile.bio = data.bio
        profile.phone_number = data.phone_number
        profile.date_of_birth = data.date_of_birth
        profile.save()
    return UserOut.model_validate(user)


@app.delete("/users/{user_id}")
@decorators.role_required([ROLES.USER, ROLES.ADMIN])
def delete_user(request, user_id: int):
    """
    Delete a user and their associated profile.

    Args:
        request: The HTTP request object
        user_id (int): The ID of the user to delete

    Returns:
        dict: Success message confirming deletion

    Raises:
        Http404: If user with specified ID doesn't exist

    Permission:
        Requires USER or ADMIN role
    """
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return {"success": True, "message": "User deleted successfully"}
