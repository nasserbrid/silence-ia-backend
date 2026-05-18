from fastapi import APIRouter, Depends

from app.models.user import User
from app.schemas.session import SessionCreate, SessionRead
from app.services.auth import get_current_user
from app.services.session import SessionService, get_session_service

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("/", response_model=list[SessionRead])
def get_history(
    current_user: User = Depends(get_current_user),
    svc: SessionService = Depends(get_session_service),
):
    return svc.get_by_user(current_user.id)


@router.post("/", response_model=SessionRead, status_code=201)
def save_session(
    data: SessionCreate,
    current_user: User = Depends(get_current_user),
    svc: SessionService = Depends(get_session_service),
):
    return svc.create(current_user.id, data)


@router.delete("/{session_id}", status_code=204)
def delete_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    svc: SessionService = Depends(get_session_service),
):
    svc.delete(session_id, current_user.id)
