from fastapi import APIRouter, Depends
from app.schemas.petition_schema import (
    PetitionRequest,
    PetitionResponse
)
from app.services.analysis_service import RealAnalysisService
from app.services.base_analysis import BaseAnalysisService

router = APIRouter()


def get_analysis_service() -> BaseAnalysisService:
    return RealAnalysisService()


@router.post("/send-petition", response_model=PetitionResponse)
async def analyze_petition(
    petition: PetitionRequest,
    service: BaseAnalysisService = Depends(get_analysis_service),
):
    return await service.process_petition(data=petition)
