import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from accounts.utils import validate_phone_number, validate_user_email


# Permssion Model
class Permission(models.Model):
    code = models.CharField(max_length=100, unique=True)  # e.g., 'can_create_user'
    description = models.TextField(blank=True)

    def __str__(self):
        return self.code


class UserManager(BaseUserManager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
    

    def create_user(self, email, phone_number, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if not phone_number:
            raise ValueError("Phone number is required")
            
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            phone_number=phone_number,
            **extra_fields
        )
        user.full_clean()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        user = self.create_user(phone_number=phone_number, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class AllUsersManager(BaseUserManager):
    def get_queryset(self):
        return super().get_queryset()  # no filter


class AuthProvider(models.TextChoices):
    PHONE = 'phone', 'Phone OTP'
    GOOGLE = 'google', 'Google OAuth'

class User(AbstractBaseUser, PermissionsMixin):
    # Core authentication fields
    email = models.EmailField(unique=True, blank=True, null=True,validators=[validate_user_email])
    is_email_verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=12, unique=True,validators=[validate_phone_number])
    auth_provider = models.CharField(
        choices=AuthProvider.choices,
        default=AuthProvider.PHONE
    )

    # System fields
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()
    all_objects = AllUsersManager()  # includes deleted

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ['email']

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.email:
            validate_user_email(self.email)
        if self.phone_number:
            validate_phone_number(self.phone_number)

    def __str__(self):
        return f"User {self.id}"



class ProfileType(models.Model):
    type = models.CharField(max_length=50, unique=True)
    metadata = models.JSONField(blank=True, null=True)
    permissions = models.ManyToManyField(Permission, blank=True, related_name="profile_types")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.type


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=30)  # Required
    last_name = models.CharField(max_length=30)   # Required
    gender = models.CharField(
        max_length=10,
        choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')]
    )  # Required
    date_of_birth = models.DateField()  # Required
    is_referred = models.BooleanField(default=False)
    profile_type = models.ForeignKey(ProfileType, on_delete=models.SET_NULL, null=True, related_name="profiles")
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def is_complete(self) -> bool:
        """Check if all required fields are filled"""
        return all([
            self.first_name,
            self.last_name,
            self.user.email,
            self.date_of_birth,
            self.gender
        ])

    def __str__(self):
        return f"Profile of {self.user.email}"




########################################### User Points related models ########################################################
class PointAction(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    points = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class UserPoints(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="points")
    points = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.points} pts"
    

# OTP  model
class OtpVerification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    identifier = models.CharField(max_length=255, db_index=True) # email or phone
    code_hash = models.CharField(max_length=128)
    salt = models.CharField(max_length=32)
    channel = models.CharField(max_length=16, choices=[("sms","sms"),("email","email")])
    expires_at = models.DateTimeField()
    attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=5)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        indexes = [
        models.Index(fields=["identifier", "is_used"]),
        models.Index(fields=["expires_at"]),
        ]


    def is_expired(self):
        return timezone.now() >= self.expires_at