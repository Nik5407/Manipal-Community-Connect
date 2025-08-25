import os, hmac, hashlib, random, string, time
from typing import Tuple
from django.conf import settings
from datetime import datetime, timedelta, timezone as dt_tz


ALPHANUM = string.digits # numeric OTP


def gen_otp(length: int) -> str:
    return "".join(random.choice(ALPHANUM) for _ in range(length))


def gen_salt(n: int = 16) -> str:
    return os.urandom(n).hex()[:32]


def hash_code(code: str, salt: str) -> str:
    return hashlib.sha256((salt + ":" + code).encode()).hexdigest()


def constant_time_eq(a: str, b: str) -> bool:
    return hmac.compare_digest(a, b)