# permissions.py
from ninja.errors import HttpError
from functools import wraps


def permission_required(*required_permissions):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.auth
            print("user in decorator",user)

            if not hasattr(user, 'profile') or not user.profile.profile_type:
                raise HttpError(403, "No profile or role associated with user")

            profile_type = user.profile.profile_type
            user_permissions = set(profile_type.permissions.values_list("code", flat=True))

            for perm in required_permissions:
                if perm not in user_permissions:
                    raise HttpError(403, f"Permission '{perm}' is required")

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


