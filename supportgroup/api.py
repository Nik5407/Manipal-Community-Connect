from ninja import Router
from typing import List, Optional
from django.shortcuts import get_object_or_404
from django.db.models import Q, F, Value
from django.db.models.functions import Concat, Coalesce
from django.db import transaction
from ninja.errors import HttpError

from .models import SupportGroup, GroupMembership, SupportGroupRoles, SupportGroupRolesChoices
from .schema import SupportGroupOut, GroupMemberOut
from manipalapp.jwt import JWTAuth

app = Router(tags=["support_groups"], auth=JWTAuth())


####
#Support Group APIs
####
@app.get("/groups/", response=List[SupportGroupOut], auth=None)
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

@app.get("/groups/search/", response=List[SupportGroupOut], auth=None)
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

@app.get("/groups/{group_id}/", response=SupportGroupOut, auth=None)
def get_support_group(request, group_id: int):
    """
    Get a specific support group by its ID.
    """
    group = get_object_or_404(SupportGroup, id=group_id)
    return SupportGroupOut.model_validate(group)


@app.post("/groups/{group_id}/join/")
@transaction.atomic
def join_group(request, group_id: int):
    """
    Join a support group.
    
    Args:
        request: The HTTP request object containing the authenticated user
        group_id: ID of the group to join
        
    Returns:
        dict: Success message
    
    Raises:
        HttpError: If user is already a member or group doesn't exist
    """
    group = get_object_or_404(SupportGroup, id=group_id)
    
    # Check if user is already a member
    if GroupMembership.objects.filter(user=request.user, group=group).exists():
        raise HttpError(400, "You are already a member of this group")
    
    # Create membership with general role
    membership = GroupMembership.objects.create(
        user=request.user,
        group=group
    )
    general_role, _ = SupportGroupRoles.objects.get_or_create(
        name=SupportGroupRolesChoices.GENERAL
    )

    membership.role.add(general_role)
    
    # Update group stats
    group.total_members = F('total_members') + 1
    group.save()
    
    return {"message": "Successfully joined the group"}


@app.delete("/groups/{group_id}/leave/")
@transaction.atomic
def leave_group(request, group_id: int):
    """
    Leave a support group.
    
    Args:
        request: The HTTP request object containing the authenticated user
        group_id: ID of the group to leave
        
    Returns:
        dict: Success message
    
    Raises:
        HttpError: If user is not a member or group doesn't exist
    """
    group = get_object_or_404(SupportGroup, id=group_id)
    
    # Get and delete membership if exists
    membership = GroupMembership.objects.filter(user=request.user, group=group).first()
    if not membership:
        raise HttpError(400, "You are not a member of this group")
    
    membership.delete()
    
    # Update group stats
    group.total_members = F('total_members') - 1
    group.save()
    
    return {"message": "Successfully left the group"}


@app.get("/groups/{group_id}/members/", response=List[GroupMemberOut], auth=None)
def list_group_members(request, group_id: int):
    """
    List all members of a support group.
    """
    group = get_object_or_404(SupportGroup, id=group_id)

    memberships = (
        GroupMembership.objects
        .filter(group=group)
        .select_related("user", "user__profile")
        .prefetch_related("role")
        .annotate(
            full_name=Concat(
                Coalesce(F("user__profile__first_name"), Value("")),
                Value(" "),
                Coalesce(F("user__profile__last_name"), Value(""))
            )
        )
    )

    members = []
    for membership in memberships:
        member_data = {
            "id": membership.user.id,
            "full_name": membership.full_name.strip(),  # avoid " " when no profile
            "email": membership.user.email,
            "roles": [role.name for role in membership.role.all()],
            "joined_at": membership.joined_at,
        }
        members.append(GroupMemberOut.model_validate(member_data))

    return members
