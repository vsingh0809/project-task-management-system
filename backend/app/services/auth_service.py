import logging

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_user(self, user_data: UserCreate) -> User:
        """
        Register a new user after validating email and username uniqueness.
        """
        normalized_email = user_data.email.lower()
        normalized_username = user_data.username.lower()

        result = await self.db.execute(
            select(User).where(
                or_(
                    User.email == normalized_email,
                    User.username == normalized_username,
                )
            )
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            if existing_user.email == normalized_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

        user = User(
            email=normalized_email,
            username=normalized_username,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name.strip() if user_data.full_name else None,
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        logger.info("User registered successfully: %s", user.email)
        return user

    async def authenticate_user(self, login_data: UserLogin) -> dict:
        """
        Authenticate a user and return an access token.
        """
        normalized_email = login_data.email.lower()

        result = await self.db.execute(
            select(User).where(User.email == normalized_email)
        )
        user = result.scalar_one_or_none()

        if user is None or not verify_password(
            login_data.password, user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated",
            )

        access_token = create_access_token(
            subject=user.id,
            extra_claims={"email": user.email},
        )

        logger.info("User logged in successfully: %s", user.email)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user,
        }