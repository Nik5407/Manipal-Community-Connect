from django.contrib import admin
from .models import (
    GroupCategory,
    SupportGroup,
    SupportGroupRoles,
    GroupMembership,
    GroupPost,
    PostAttachment,
    PostInteraction
)


@admin.register(GroupCategory)
class GroupCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active", "is_featured", "is_deleted", "created_at")
    list_filter = ("is_active", "is_featured", "is_deleted", "created_at")
    search_fields = ("name", "description")
    ordering = ("-created_at",)


@admin.register(SupportGroup)
class SupportGroupAdmin(admin.ModelAdmin):
    list_display = (
        "id", "title", "category", "rating",
        "total_members", "total_experts", "total_posts", "total_sessions",
        "growth_percentage", "created_at"
    )
    list_filter = ("category", "created_at")
    search_fields = ("title", "description")
    ordering = ("-created_at",)


@admin.register(SupportGroupRoles)
class SupportGroupRolesAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "group", "joined_at")
    list_filter = ("group", "joined_at")
    search_fields = ("user__username", "group__title")
    ordering = ("-joined_at",)
    filter_horizontal = ("role",)  # ManyToManyField better UI


@admin.register(GroupPost)
class GroupPostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "group", "category", "like_count", "reply_count", "num_reads", "created_at")
    list_filter = ("category", "group", "created_at")
    search_fields = ("title", "content", "author__username", "group__title")
    ordering = ("-created_at",)


@admin.register(PostAttachment)
class PostAttachmentAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "file", "uploaded_at")
    list_filter = ("uploaded_at",)
    search_fields = ("post__title",)


@admin.register(PostInteraction)
class PostInteractionAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "user", "type", "created_at")
    list_filter = ("type", "created_at")
    search_fields = ("post__title", "user__username")
    ordering = ("-created_at",)
