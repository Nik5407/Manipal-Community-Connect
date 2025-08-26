from datetime import timedelta

from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from .sender import OtpSender
from accounts.utils import gen_otp, gen_salt, hash_code, constant_time_eq
from manipalapp.settings import OTP_LOGIN_SETTINGS
from accounts.models import User, UserProfile
from accounts.models import OtpVerification


class OtpService:
    def __init__(self,sender:OtpSender):
        self.sender=sender
        self.cfg=OTP_LOGIN_SETTINGS

    # ---- Rate limiting helpers ----
    def _cooldown_key(self, identifier: str) -> str:
        return f"otp:cooldown:{identifier}"


    def _daily_key(self, identifier: str) -> str:
        today = timezone.now().date().isoformat()
        return f"otp:daily:{identifier}:{today}"


    def _check_and_increment_limits(self, identifier: str):
        # Cooldown
        if cache.get(self._cooldown_key(identifier)):
            raise ValueError("Please wait before requesting another OTP.")

        # Daily cap
        daily_key = self._daily_key(identifier)
        count = cache.get(daily_key, 0)
        if count >= self.cfg["DAILY_REQUEST_LIMIT"]:
            raise ValueError("Daily OTP request limit reached. Try again tomorrow.")

        cache.set(daily_key, count + 1, 60 * 60 * 24)
        cache.set(self._cooldown_key(identifier), 1, self.cfg["RESEND_COOLDOWN"])  # cooldown seconds


    # ---- Public API ----
    def request_otp(self, identifier: str, channel: str = "sms") -> None:
        self._check_and_increment_limits(identifier)

        code = gen_otp(self.cfg["OTP_LENGTH"])
        salt = gen_salt()
        code_h = hash_code(code, salt)
        expires = timezone.now() + timedelta(seconds=self.cfg["TTL_SECONDS"])

        # Invalidate previous unused challenges for same identifier
        OtpVerification.objects.filter(identifier=identifier, is_used=False).update(is_used=True)

        OtpVerification.objects.create(
            identifier=identifier,
            code_hash=code_h,
            salt=salt,
            channel=channel,
            expires_at=expires,
            max_attempts=self.cfg["MAX_ATTEMPTS"],
        )

        msg = f"Your {settings.OTP_LOGIN_SETTINGS.get('JWT_ISSUER','app')} login OTP is {code}. " \
            f"It expires in {self.cfg['TTL_SECONDS']//60} minutes. Do not share this code."
        self.sender.send(identifier, msg)


    def verify_otp(self, identifier: str, code: str, is_email_verification: bool = False) -> dict:
        # Fetch the latest active challenge
        try:
            ch = (OtpVerification.objects
                .filter(identifier=identifier, is_used=False)
                .latest("created_at"))
        except OtpVerification.DoesNotExist:
            raise ValueError("No active OTP. Please request a new one.")

        if ch.is_expired():
            ch.is_used = True
            ch.save(update_fields=["is_used"])
            raise ValueError("OTP expired. Request a new one.")

        if ch.attempts >= ch.max_attempts:
            ch.is_used = True
            ch.save(update_fields=["is_used"])
            raise ValueError("Too many attempts. Request a new OTP.")
        
        ch.attempts += 1
        ch.save(update_fields=["attempts"])

        if not constant_time_eq(ch.code_hash, hash_code(code, ch.salt)):
            remaining = max(0, ch.max_attempts - ch.attempts)
            raise ValueError(f"Invalid OTP. {remaining} attempts left.")

        # Success: mark used
        ch.is_used = True
        ch.save(update_fields=["is_used"])

        if is_email_verification:
            # This is email verification flow
            try:
                user = User.objects.get(email=identifier)
                user.is_email_verified = True
                user.save(update_fields=["is_email_verified"])
                return {"success": True, "message": "Email verified successfully"}
            except User.DoesNotExist:
                raise ValueError("User not found")
        else:
            # This is phone login flow
            user, created = User.objects.get_or_create(phone_number=identifier)
            
            # Check if profile is complete
            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "first_name": "",
                    "last_name": "",
                    "gender": "other",
                    "date_of_birth": "2000-01-01"  # placeholder
                }
            )

            if not profile.is_complete():
                return {
                    "user_exists": True,
                    "profile_complete": False,
                    "verification_id": str(ch.id),  # Send verification ID for profile completion
                    "message": "Please complete your profile"
                }
            
            # Profile is complete, return tokens
            return {
                "user_exists": True,
                "profile_complete": True,
                "tokens": self._issue_token(user),
                "is_email_verified": user.is_email_verified
            }


    def complete_profile(self, verification_id: str, profile_data: dict) -> dict:
        """
        Complete user profile after OTP verification.
        
        Args:
            verification_id: The ID of the OTP verification
            profile_data: Dictionary containing profile fields:
                - first_name
                - last_name
                - email
                - date_of_birth
                - gender
                - is_referred (optional)
        
        Returns:
            dict: JWT tokens if successful
        """
        try:
            verification = OtpVerification.objects.get(id=verification_id)
            if verification.is_expired():
                raise ValueError("Verification expired. Please request new OTP.")
                
            # Create or get user
            user, _ = self._get_or_create_user(verification.identifier)
            
            # Create or update profile
            profile = user.profile
            profile.first_name = profile_data['first_name']
            profile.last_name = profile_data['last_name']
            profile.date_of_birth = profile_data['date_of_birth']
            profile.gender = profile_data['gender']
            profile.is_referred = profile_data.get('is_referred', False)
            user.email = profile_data['email']
            user.save()
            profile.save()

            
            # Return tokens for automatic login
            return self._issue_token(user)
            
        except OtpVerification.DoesNotExist:
            raise ValueError("Invalid verification ID")
        except Exception as e:
            raise ValueError(f"Profile creation failed: {str(e)}")

    def _get_or_create_user(self, identifier: str) -> User:
        # Can include email as identifier as well in future 
        try:
            # If it's a valid email
            validate_email(identifier)
            user, _ = User.objects.get_or_create(
                email=identifier
            )
        except ValidationError:
            # Otherwise treat it as phone number
            user, _ = User.objects.get_or_create(
                phone_number=identifier
            )

        return user,_

    def _issue_token(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }



