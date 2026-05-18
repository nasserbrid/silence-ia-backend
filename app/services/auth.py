import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import Token
from app.services.password import PasswordService, get_password_service
from app.services.token import TokenService, get_token_service

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class AuthService:
    def __init__(self, password_svc: PasswordService, token_svc: TokenService):
        self.password = password_svc
        self.token = token_svc

    def authenticate(self, email: str, password: str, db: Session) -> Token:
        user = UserRepository(db).get_by_email(email)
        if not user or not self.password.verify(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Compte désactivé",
            )
        token = self.token.create({"sub": user.email, "role": user.role})
        return Token(access_token=token)


def get_auth_service(
    password_svc: PasswordService = Depends(get_password_service),
    token_svc: TokenService = Depends(get_token_service),
) -> AuthService:
    return AuthService(password_svc, token_svc)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    token_svc: TokenService = Depends(get_token_service),
) -> User:
    token_data = token_svc.decode(token)
    user = UserRepository(db).get_by_email(token_data.email)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs",
        )
    return current_user
