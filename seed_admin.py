import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.session import Session  # noqa: ensure all models are registered
from app.services.password import PasswordService

Base.metadata.create_all(bind=engine)

_password_svc = PasswordService()

EMAIL = "admin@coachingprisedeparole.fr"
PASSWORD = "changeme123!"

db = SessionLocal()

existing = db.query(User).filter(User.email == EMAIL).first()
if existing:
    print(f"L'utilisateur {EMAIL} existe déjà.")
else:
    admin = User(
        email=EMAIL,
        password_hash=_password_svc.hash(PASSWORD),
        role="admin",
        is_active=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print(f"Admin créé : {EMAIL} (id={admin.id})")
    print(f"Mot de passe initial : {PASSWORD}")
    print("Pensez à le changer après la première connexion.")

db.close()
