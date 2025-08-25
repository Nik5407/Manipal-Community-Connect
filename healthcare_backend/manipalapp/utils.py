from rest_framework_simplejwt.tokens import AccessToken


def get_jwt_token(user):
    """
    Return Access token for user
    """
    token = AccessToken.for_user(user)
    return str(token)
