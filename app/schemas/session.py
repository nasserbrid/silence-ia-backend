from datetime import datetime
from pydantic import BaseModel


class SessionCreate(BaseModel):
    type_discours: str
    type_discours_label: str
    duree_prevue_min: float
    duree_effective_sec: int
    transcription: str
    analyse: str
    word_count: int = 0


class SessionRead(SessionCreate):
    id: int
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalyzeRequest(BaseModel):
    type_discours: str
    type_discours_label: str
    duree_min: str
    transcript: str
    images: list[str] = []
    audio_stats: dict = {}
    visual_stats: dict = {}


class AnalyzeResponse(BaseModel):
    analyse: str
