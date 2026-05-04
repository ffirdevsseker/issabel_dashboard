from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import verify_password, create_access_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserMe

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.kullanici_adi == credentials.username).first()

    if not user or not verify_password(credentials.password, user.sifre_hash):
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
        subject=user.kullanici_adi,
        role=user.role_name,
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
