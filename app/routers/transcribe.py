from fastapi import APIRouter, UploadFile, File, Depends
from openai import AsyncOpenAI
from app.services.auth import get_current_user
from app.core.config import settings

router = APIRouter()


@router.post("/api/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    content = await audio.read()
    result = await client.audio.transcriptions.create(
        model="whisper-1",
        file=(audio.filename or "recording.webm", content, audio.content_type or "audio/webm"),
        language="fr",
    )
    return {"transcript": result.text}
