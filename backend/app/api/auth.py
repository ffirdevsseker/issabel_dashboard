from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.security import verify_password, create_access_token
from app.db.async_session import get_async_db
from app.db.health import check_db_connection
from app.models.role import Rol
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserMe

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_async_db)):
    await check_db_connection()

    stmt = (
        select(User, Rol.ad)
        .join(Rol, Rol.id == User.rol_id)
        .where(User.kullanici_adi == credentials.username)
    )

    try:
        result = await db.execute(stmt)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Veritabani baglantisi gecici olarak kullanilamiyor",
        ) from exc

    row = result.first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı adı veya şifre hatalı",
        )

    user, role_name = row
    if not verify_password(credentials.password, user.sifre_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı adı veya şifre hatalı",
        )

    if user.silindi_mi:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hesabınız pasif durumda",
        )

    token = create_access_token(
        user_id=str(user.id),
        username=user.kullanici_adi,
        role=role_name,
        extension=user.dahili_no,
    )
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserMe)
def read_me(current_user: User = Depends(get_current_user)):
    return UserMe(
        id=str(current_user.id),
        username=current_user.kullanici_adi,
        full_name=current_user.ad_soyad,
        extension=current_user.dahili_no,
        role=current_user.role_name,
        is_active=not current_user.silindi_mi,
    )
