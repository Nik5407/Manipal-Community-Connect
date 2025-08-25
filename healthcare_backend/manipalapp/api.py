from ninja import NinjaAPI
from django.contrib.auth.decorators import login_required
from accounts.api import app as accounts_router
from manipalapp.jwt import JWTAuth

# Configure API with security scheme
api = NinjaAPI(
    title="Healthcare API",
    version="1.0.0",
    description="""
    Healthcare API with JWT Authentication.
    
    To use the API:
    1. Register a new user at /api/v1/accounts/register/
    2. Get JWT token at /api/v1/auth/token/
    3. Use the token in the Authorization header: Bearer <your_token>
    4. Refresh token at /api/v1/auth/token/refresh/ when needed
    """,
    docs_url="docs",
    openapi_url="openapi.json",
    auth=JWTAuth(),
    csrf=False,  # Disable CSRF for API endpoints
    openapi_extra={
        "components": {
            "securitySchemes": {
                "Bearer": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
        },
        "security": [{"Bearer": []}]
    }
)

# Add routers
api.add_router("/accounts", accounts_router)
