from ninja import Router
from typing import List, Optional
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import SupportGroup
from .schema import SupportGroupOut
from manipalapp.jwt import JWTAuth

app = Router(tags=["support_groups"], auth=JWTAuth())

@app.get("/", response=List[SupportGroupOut], auth=None)
def list_support_groups(request):
    """
    List all support groups in the system.

    Args:
        request: The HTTP request object

    Returns:
        List[SupportGroupOut]: List of all support groups with their details
    """
    groups = SupportGroup.objects.select_related('category').all()
    return [SupportGroupOut.model_validate(group) for group in groups]

@app.get("/search/", response=List[SupportGroupOut], auth=None)
def search_support_groups(
    request,
    query: str,
    sort_by: Optional[str] = None
):
    """
    Search support groups based on various criteria.

    Args:
        request: The HTTP request object
        query: Search term to match against title and description
        category_id: Optional filter by category ID
        min_rating: Optional filter for minimum rating
        sort_by: Optional sorting field (created_at, rating, total_members)

    Returns:
        List[SupportGroupOut]: List of matching support groups
    """
    # Start with all groups
    groups = SupportGroup.objects.select_related('category')

    # Apply search query
    if query:
        groups = groups.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )

    # Apply sorting
    if sort_by:
        sort_mapping = {
            'created_at': '-created_at',  # Newest first
            'rating': '-rating',  # Highest rated first
            'members': '-total_members',  # Most members first
            'experts': '-total_experts',  # Most experts first
            'posts': '-total_posts',  # Most posts first
            'sessions': '-total_sessions',  # Most sessions first
        }
        if sort_by in sort_mapping:
            groups = groups.order_by(sort_mapping[sort_by])

    return [SupportGroupOut.model_validate(group) for group in groups]