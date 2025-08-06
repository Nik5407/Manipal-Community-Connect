from ninja.errors import HttpError
from functools import wraps


def role_required(allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrap(request, *args, **kwargs):

            user = request.auth  # JWTAuth will set request.auth to the logged-in user
            print("user", user)
            if not hasattr(user, 'profile') or not user.profile.profile_type:
                raise HttpError(403, "No profile or role associated with user")

            user_role = user.profile.profile_type.type  # Get the role name (e.g., "admin")
            print("user_role", user_role)
            if user_role not in allowed_roles:
                raise HttpError(403, f"Access denied for role: {user_role}")
            return func(request, *args, **kwargs)
        return wrap
    return decorator

