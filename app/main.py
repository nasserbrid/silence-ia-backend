from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.limiter import limiter
from app.core.logging import setup_logging
from app.database import Base, engine
from app.models import user, session  # noqa: F401 — force table registration
from app.routers import auth, users, analyze, history

setup_logging()
settings.validate()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Nicolas IA — API",
    description="Backend de l'outil d'analyse de prise de parole",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(analyze.router)
app.include_router(history.router)


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}
