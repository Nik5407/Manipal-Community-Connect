import os, hmac, hashlib, random, string, re
from typing import Tuple
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


ALPHANUM = string.digits # numeric OTP


def gen_otp(length: int) -> str:
    return "".join(random.choice(ALPHANUM) for _ in range(length))


def gen_salt(n: int = 16) -> str:
    return os.urandom(n).hex()[:32]


def hash_code(code: str, salt: str) -> str:
    return hashlib.sha256((salt + ":" + code).encode()).hexdigest()


def constant_time_eq(a: str, b: str) -> bool:
    return hmac.compare_digest(a, b)



def validate_phone_number(value):
    # Example: Indian numbers only, 10 digits
    pattern = re.compile(r'^\d{10,12}$')
    if not pattern.match(value):
        raise ValidationError("Phone number must be 10-12 digits.")

def validate_user_email(value):
    try:
        validate_email(value)
    except ValidationError:
        raise ValidationError("Enter a valid email address.")
