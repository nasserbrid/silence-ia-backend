from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.services.password import PasswordService, get_password_service


class UserService:
    def __init__(self, repo: UserRepository, password_svc: PasswordService):
        self.repo = repo
        self.password = password_svc

    def get_all(self) -> list[User]:
        return self.repo.get_all()

    def get_by_id(self, user_id: int) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")
        return user

    def create(self, data: UserCreate) -> User:
        if self.repo.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Un compte existe déjà avec cet email",
            )
        password_hash = self.password.hash(data.password)
        return self.repo.create(email=data.email, password_hash=password_hash, role=data.role)

    def update(self, user_id: int, data: UserUpdate) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")
        updates = data.model_dump(exclude_none=True)
        if "password" in updates:
            updates["password_hash"] = self.password.hash(updates.pop("password"))
        if "email" in updates and updates["email"] != user.email:
            if self.repo.get_by_email(updates["email"]):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email déjà utilisé")
        return self.repo.update(user, **updates)

    def delete(self, user_id: int) -> None:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")
        self.repo.delete(user)


def get_user_service(
    db: Session = Depends(get_db),
    password_svc: PasswordService = Depends(get_password_service),
) -> UserService:
    return UserService(UserRepository(db), password_svc)
