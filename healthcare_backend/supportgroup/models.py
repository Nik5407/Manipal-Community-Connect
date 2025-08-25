# from django.db import models
# from django.utils import timezone
# from django.conf import settings

# User = settings.AUTH_USER_MODEL


# # -----------------------
# # Group Category model
# # -----------------------
# class GroupCategory(models.Model):
#     name = models.CharField(max_length=255)
#     description = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     is_active = models.BooleanField(default=True)
#     is_deleted = models.BooleanField(default=False)
#     is_featured = models.BooleanField(default=False)



# # -----------------------
# # Support Group
# # -----------------------
# class SupportGroup(models.Model):
#     title = models.CharField(max_length=255)
#     description = models.TextField()
#     category = models.ForeignKey(GroupCategory, on_delete=models.CASCADE, related_name="groups")

#     rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
#     group_image = models.ImageField(upload_to="group_images/", blank=True, null=True)

#     # Cached stats (Update them using F() expressions in functions)
#     total_members = models.PositiveIntegerField(default=0)
#     total_experts = models.PositiveIntegerField(default=0)
#     total_posts = models.PositiveIntegerField(default=0)
#     total_sessions = models.PositiveIntegerField(default=0)

#     # Growth percentage (calculated from total_members, total_posts, total_sessions ???)
#     growth_percentage = models.FloatField(default=0.0)

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.title
    
# class SupportGroupRolesChoices(models.TextChoices):
#     GENERAL = "general", "General"
#     EXPERT = "expert", "Expert"
#     MODERATOR = "moderator", "Moderator"

# class SupportGroupRoles(models.Model):
#     name = models.CharField(
#         max_length=20,
#         choices=SupportGroupRolesChoices.choices,
#         unique=True
#     )

# # -----------------------
# # Group Membership (User joins group)
# # -----------------------
# class GroupMembership(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_memberships")
#     group = models.ForeignKey(SupportGroup, on_delete=models.CASCADE, related_name="memberships")

#     role=models.ManyToManyField(SupportGroupRoles, related_name="group_memberships")

#     joined_at = models.DateTimeField(default=timezone.now)

#     class Meta:
#         unique_together = ("user", "group")

#     def __str__(self):
#         return f"{self.user} in {self.group}"

# ########################################### Post related models ########################################################

# # -----------------------
# # Group Posts (Feed)
# # -----------------------
# class GroupPost(models.Model):
#     group = models.ForeignKey(SupportGroup, on_delete=models.CASCADE, related_name="posts")
#     author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_posts")

#     title = models.CharField(max_length=255)
#     content = models.TextField(blank=True, null=True)
#     category = models.CharField(max_length=50, choices=GroupCategory.choices, default=GroupCategory.GENERAL)

#     # expert_number = models.PositiveIntegerField(default=0)  # optional, if post is expert-driven

#     # Cached stats / Update them using F() expressions
#     like_count = models.PositiveIntegerField(default=0)
#     reply_count = models.PositiveIntegerField(default=0)
#     num_reads = models.PositiveIntegerField(default=0)

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Post by {self.author} in {self.group}"


# # -----------------------
# # Post Attachments
# # -----------------------
# class PostAttachment(models.Model):
#     post = models.ForeignKey(GroupPost, on_delete=models.CASCADE, related_name="attachments")
#     file = models.FileField(upload_to="group_posts/attachments/") # Integrate s3 or something else later 
#     uploaded_at = models.DateTimeField(auto_now_add=True)

# # -----------------------
# # Post Interactions (Like, Reply, Share)  
# # -----------------------

# # Can create separte model as well interactions type
# class InteractionType(models.TextChoices):
#     LIKE = "like", "Like"
#     SHARE = "share", "Share"

# class PostInteraction(models.Model):
#     post = models.ForeignKey(GroupPost, on_delete=models.CASCADE, related_name="interactions")
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     type = models.CharField(max_length=10, choices=InteractionType.choices)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ("post", "user", "type")

# class PostReply(models.Model):
#     post = models.ForeignKey(GroupPost, on_delete=models.CASCADE, related_name="replies")
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Reply by {self.user} to {self.post}"
    



# # from rest_framework_simplejwt.tokens import AccessToken
# # from django.contrib.auth import get_user_model

# # User = get_user_model()
# # def get_jwt_token(user):
# #     """
# #     Return Access token for user
# #     """
# #     token = AccessToken.for_user(user)
# #     return str(token)



# # user=User.objects.get(email="nikunj@launchxlabs.ai")
# # print("user",user)
# # print(get_jwt_token(user))