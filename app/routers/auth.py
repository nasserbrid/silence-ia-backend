import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.limiter import limiter
from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserRead
from app.services.auth import AuthService, get_auth_service, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(
    request: Request,
    data: LoginRequest,
    db: Session = Depends(get_db),
    auth_svc: AuthService = Depends(get_auth_service),
):
    try:
        token = auth_svc.authenticate(data.email, data.password, db)
        logger.info("Connexion réussie : %s", data.email)
        return token
    except Exception:
        logger.warning("Échec de connexion pour : %s", data.email)
        raise


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user
