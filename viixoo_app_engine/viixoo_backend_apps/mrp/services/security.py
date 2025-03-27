"""This module contains functions for managing application security, including the creation and verification of JWT tokens."""

from datetime import datetime, timedelta, timezone
from typing import Any
import secrets

import jwt
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = "HS256"
SECRET_KEY: str = secrets.token_urlsafe(32)


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    """
    Create a JWT access token for the given subject.

    :param subject: The subject of the token (e.g., a user ID).
    :param expires_delta: The token's expiration time.
    :return: The encoded JWT token.
    """
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify if a plaintext password matches an encrypted password.

    :param plain_password: Plaintext password.
    :param hashed_password: Encrypted password.
    :return: True if a match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Encrypts a password using the configured encryption context.

    :param password: Password to encrypt.
    :return: Encrypted password.
    """
    return pwd_context.hash(password)
