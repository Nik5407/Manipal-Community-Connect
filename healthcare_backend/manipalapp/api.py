from ninja import NinjaAPI
from django.contrib.auth.decorators import login_required
from accounts.api import app as accounts_router

api = NinjaAPI(
    title="Healthcare API",
    version="1.0.0",
    docs_url="docs",
    openapi_url="openapi.json",
    docs_decorator=login_required
)

api.add_router("/accounts", accounts_router)
