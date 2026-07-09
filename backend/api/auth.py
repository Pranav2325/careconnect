# backend/api/auth.py
# Authentication routes — register, login, get current user

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from backend.db.database import get_db
from backend.db.models import User, Family
from backend.services.auth_service import auth_service

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# OAuth2PasswordBearer tells FastAPI where to find the token
# tokenUrl = the endpoint that issues tokens (our login endpoint)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ── Pydantic Schemas ──────────────────────────────────────────────

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    family_name: str
    role: str = "member"  # "admin" or "member"

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    family_id: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# ── Dependency — Get Current User ─────────────────────────────────
# This function is used as a dependency in protected routes
# Any route that needs authentication calls Depends(get_current_user)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Extracts and verifies the JWT token from the request header.
    Returns the current logged-in user.
    Raises 401 if token is invalid or expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = auth_service.verify_token(token)
    if payload is None:
        raise credentials_exception

    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user


# ── Routes ───────────────────────────────────────────────────────

@router.post("/register", response_model=UserResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new family member.
    Creates family if it doesn't exist.
    """
    # Check if email already exists
    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Get or create family
    family = db.query(Family).filter(
        Family.name == user_data.family_name
    ).first()
    if not family:
        family = Family(name=user_data.family_name)
        db.add(family)
        db.commit()
        db.refresh(family)

    # Create user with hashed password
    user = User(
        family_id=family.id,
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        hashed_password=auth_service.hash_password(user_data.password),
        role=user_data.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with email and password.
    Returns JWT token on success.

    OAuth2PasswordRequestForm expects:
    - username (we use email here)
    - password
    """
    # Find user by email
    user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    # Verify password
    if not user or not auth_service.verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create JWT token
    access_token = auth_service.create_access_token(
        data={"sub": user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns the currently logged-in user's info.
    Uses JWT token from request header.
    """
    return current_user