from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user.
    """
    auth_service = AuthService(db)
    return await auth_service.register_user(user_data)


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user and return JWT access token.
    """
    auth_service = AuthService(db)
    return await auth_service.authenticate_user(login_data)