from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models.session import Session
from app.repositories.session import SessionRepository
from app.schemas.session import SessionCreate


class SessionService:
    def __init__(self, repo: SessionRepository):
        self.repo = repo

    def get_by_user(self, user_id: int) -> list[Session]:
        return self.repo.get_by_user(user_id)

    def create(self, user_id: int, data: SessionCreate) -> Session:
        return self.repo.create(user_id=user_id, **data.model_dump())

    def delete(self, session_id: int, user_id: int) -> None:
        session = self.repo.get_by_id(session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session introuvable")
        if session.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès interdit")
        self.repo.delete(session)


def get_session_service(db: DBSession = Depends(get_db)) -> SessionService:
    return SessionService(SessionRepository(db))
