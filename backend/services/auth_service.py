# backend/services/auth_service.py
# Handles password hashing and JWT token creation/verification

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from backend.core.config import settings

# CryptContext handles password hashing
# bcrypt is the algorithm — industry standard, slow by design
# (slow = harder for attackers to brute force)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def hash_password(self, password: str) -> str:
        """
        Converts plain password to secure hash.
        We never store the actual password — only this hash.
        """
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Checks if entered password matches stored hash.
        Returns True if match, False if not.
        """
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict) -> str:
        """
        Creates a JWT token containing user data.
        Token expires after ACCESS_TOKEN_EXPIRE_MINUTES (set in config).

        Why expiry? If token is stolen, it becomes useless after expiry.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})

        # jwt.encode signs the token with our SECRET_KEY
        # Only our server can create valid tokens
        token = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return token

    def verify_token(self, token: str) -> Optional[dict]:
        """
        Decodes and verifies a JWT token.
        Returns the data inside the token if valid.
        Returns None if invalid or expired.
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError:
            return None


# Single instance
auth_service = AuthService()