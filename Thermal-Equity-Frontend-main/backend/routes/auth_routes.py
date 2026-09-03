from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field, field_validator
from fastapi import APIRouter, HTTPException, status, Depends

from backend.database.mongodb import find_user_by_email, create_user
from backend.services.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)

router = APIRouter(tags=["Authentication"])

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full Name")
    email: str = Field(..., description="Valid Email Address")
    password: str = Field(..., min_length=6, max_length=128, description="Password (at least 6 characters)")

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        clean = v.strip().lower()
        if not EMAIL_REGEX.match(clean):
            raise ValueError("Invalid email address format")
        return clean


class LoginRequest(BaseModel):
    email: str = Field(..., description="Registered Email Address")
    password: str = Field(..., min_length=1, description="Account Password")

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        clean = v.strip().lower()
        if not clean or "@" not in clean:
            raise ValueError("Please provide a valid email address")
        return clean


class UserResponse(BaseModel):
    id: str | None = None
    name: str
    email: str
    role: str = "analyst"
    created_at: str | None = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    message: str


# --- Core Registration Handler ---
async def handle_register(payload: RegisterRequest) -> dict[str, Any]:
    clean_email = payload.email.strip().lower()

    # Check if user already exists in MongoDB Atlas / database
    try:
        existing_user = await find_user_by_email(clean_email)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail="Authentication service unavailable") from exc
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists. Please sign in.",
        )

    # Hash password securely with bcrypt
    password_hash = get_password_hash(payload.password)

    # Create new user record in MongoDB Atlas
    user_doc = {
        "name": payload.name.strip(),
        "email": clean_email,
        "password_hash": password_hash,
        "role": "analyst",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        created = await create_user(user_doc)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail="Authentication service unavailable") from exc

    # Generate JWT Token
    token_payload = {
        "sub": clean_email,
        "name": payload.name.strip(),
        "email": clean_email,
        "role": "analyst",
    }
    try:
        access_token = create_access_token(token_payload)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail="Authentication service unavailable") from exc

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(created.get("_id", created.get("id", ""))),
            "name": created.get("name", payload.name.strip()),
            "email": clean_email,
            "role": created.get("role", "analyst"),
            "created_at": created.get("created_at"),
        },
        "message": "Municipal Analyst account registered successfully in MongoDB Atlas.",
    }


# --- Core Login Handler ---
async def handle_login(payload: LoginRequest) -> dict[str, Any]:
    clean_email = payload.email.strip().lower()

    # Find user in MongoDB Atlas
    try:
        user = await find_user_by_email(clean_email)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail="Authentication service unavailable") from exc
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password hash
    password_hash = user.get("password_hash", "")
    if not verify_password(payload.password, password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate JWT Token
    token_payload = {
        "sub": clean_email,
        "name": user.get("name", "Climate Analyst"),
        "email": clean_email,
        "role": user.get("role", "analyst"),
    }
    try:
        access_token = create_access_token(token_payload)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail="Authentication service unavailable") from exc

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.get("_id", user.get("id", ""))),
            "name": user.get("name", "Climate Analyst"),
            "email": clean_email,
            "role": user.get("role", "analyst"),
            "created_at": user.get("created_at"),
        },
        "message": "Login successful. Authenticated with MongoDB Atlas.",
    }


# Endpoints mounted with both /api/auth and /auth
@router.post(
    "/api/auth/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new municipal user",
)
@router.post(
    "/auth/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def register(payload: RegisterRequest):
    return await handle_register(payload)


@router.post(
    "/api/auth/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="User login with email and password",
)
@router.post(
    "/auth/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def login(payload: LoginRequest):
    return await handle_login(payload)


@router.get(
    "/api/auth/me",
    response_model=UserResponse,
    summary="Get current authenticated user profile",
)
@router.get(
    "/auth/me",
    response_model=UserResponse,
    include_in_schema=False,
)
async def get_me(current_user: dict[str, Any] = Depends(get_current_user)):
    return {
        "id": current_user.get("id", ""),
        "name": current_user.get("name", "Climate Analyst"),
        "email": current_user.get("email", ""),
        "role": current_user.get("role", "analyst"),
        "created_at": current_user.get("created_at"),
    }
