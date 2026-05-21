import os
from dotenv import load_dotenv

load_dotenv()

_INSECURE_SECRET = "change_me_in_production"


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", _INSECURE_SECRET)
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "claude-haiku-4-5")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    def validate(self) -> None:
        if self.SECRET_KEY == _INSECURE_SECRET:
            raise RuntimeError(
                "SECRET_KEY non configurée. "
                "Définissez une valeur sécurisée dans le fichier .env."
            )
        if not self.ANTHROPIC_API_KEY:
            raise RuntimeError(
                "ANTHROPIC_API_KEY non configurée. "
                "Définissez votre clé dans le fichier .env."
            )


settings = Settings()
