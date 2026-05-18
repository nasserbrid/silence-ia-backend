from fastapi import APIRouter, Depends

from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.auth import get_admin_user
from app.services.user import UserService, get_user_service

router = APIRouter(prefix="/admin/users", tags=["admin"])


@router.get("", response_model=list[UserRead])
def get_all(
    svc: UserService = Depends(get_user_service),
    _: User = Depends(get_admin_user),
):
    return svc.get_all()


@router.post("", response_model=UserRead, status_code=201)
def create(
    data: UserCreate,
    svc: UserService = Depends(get_user_service),
    _: User = Depends(get_admin_user),
):
    return svc.create(data)


@router.patch("/{user_id}", response_model=UserRead)
def update(
    user_id: int,
    data: UserUpdate,
    svc: UserService = Depends(get_user_service),
    _: User = Depends(get_admin_user),
):
    return svc.update(user_id, data)


@router.delete("/{user_id}", status_code=204)
def delete(
    user_id: int,
    svc: UserService = Depends(get_user_service),
    _: User = Depends(get_admin_user),
):
    svc.delete(user_id)
