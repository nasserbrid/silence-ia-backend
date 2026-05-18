from fastapi import APIRouter, Depends

from app.models.user import User
from app.schemas.session import AnalyzeRequest, AnalyzeResponse
from app.services.analyze import AnalyzeService, get_analyze_service
from app.services.auth import get_current_user

router = APIRouter(prefix="/api", tags=["analyze"])


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(
    request: AnalyzeRequest,
    svc: AnalyzeService = Depends(get_analyze_service),
    _: User = Depends(get_current_user),
):
    return AnalyzeResponse(analyse=svc.analyze(request))
