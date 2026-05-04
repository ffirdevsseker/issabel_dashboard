from typing import Iterable, List, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Geçersiz veya süresi dolmuş token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(credentials.credentials)
        username = payload.get("sub")
        if not username:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.kullanici_adi == username).first()
    if not user or user.silindi_mi:
        raise credentials_exception
    return user


def require_role(roles: Iterable[str]) -> Callable[..., User]:
    allowed: List[str] = list(roles)

    def _checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role_name not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Bu işlem için yetkiniz yok (gerekli: {', '.join(allowed)})",
            )
        return current_user

    return _checker


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role_name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu işlem için yönetici yetkisi gereklidir",
        )
    return current_user


def require_supervisor(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role_name not in ("supervisor", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu işlem için süpervizör veya yönetici yetkisi gereklidir",
        )
    return current_user
