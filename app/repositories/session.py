from sqlalchemy.orm import Session as DBSession
from app.models.session import Session


class SessionRepository:
    def __init__(self, db: DBSession):
        self.db = db

    def get_by_id(self, session_id: int) -> Session | None:
        return self.db.query(Session).filter(Session.id == session_id).first()

    def get_by_user(self, user_id: int) -> list[Session]:
        return (
            self.db.query(Session)
            .filter(Session.user_id == user_id)
            .order_by(Session.created_at.desc())
            .all()
        )

    def create(self, user_id: int, **kwargs) -> Session:
        session = Session(user_id=user_id, **kwargs)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def delete(self, session: Session) -> None:
        self.db.delete(session)
        self.db.commit()
