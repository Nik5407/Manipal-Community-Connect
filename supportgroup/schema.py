from ninja import Schema
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

class GroupMemberOut(Schema):
    id: int
    full_name: str
    email: str
    roles: List[str]
    joined_at: datetime

class GroupCategoryOut(Schema):
    id: int
    name: str
    description: str

class SupportGroupOut(Schema):
    id: int
    title: str
    description: str
    category: GroupCategoryOut
    rating: Decimal
    group_image: Optional[str]
    total_members: int
    total_experts: int
    total_posts: int
    total_sessions: int
    growth_percentage: float
    created_at: datetime
    updated_at: datetime
