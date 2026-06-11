import base64
import hashlib
import hmac
import os

from app.core.config import settings

_PASSWORD_ITERATIONS = 600_000


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        _PASSWORD_ITERATIONS,
    )
    return "pbkdf2_sha256${}${}${}".format(
        _PASSWORD_ITERATIONS,
        base64.b64encode(salt).decode("utf-8"),
        base64.b64encode(derived_key).decode("utf-8"),
    )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        algorithm, iterations_text, salt_text, expected_text = hashed_password.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        iterations = int(iterations_text)
        salt = base64.b64decode(salt_text.encode("utf-8"))
        expected = base64.b64decode(expected_text.encode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return False

    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt,
        iterations,
    )
    return hmac.compare_digest(derived_key, expected)


def create_access_token(user_id: int) -> str:
    payload = str(user_id).encode("utf-8")
    signature = hmac.new(
        settings.token_secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()
    token = f"{user_id}:{signature}".encode("utf-8")
    return base64.urlsafe_b64encode(token).decode("utf-8")


def decode_access_token(token: str) -> int | None:
    try:
        decoded = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
        user_id_text, provided_signature = decoded.split(":", 1)
        payload = user_id_text.encode("utf-8")
        expected_signature = hmac.new(
            settings.token_secret.encode("utf-8"),
            payload,
            hashlib.sha256,
        ).hexdigest()
    except (ValueError, UnicodeDecodeError):
        return None

    if not hmac.compare_digest(provided_signature, expected_signature):
        return None

    try:
        return int(user_id_text)
    except ValueError:
        return None
