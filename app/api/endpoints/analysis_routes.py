from fastapi import APIRouter, Depends, HTTPException
import os
from app.schemas.petition_schema import PetitionRequest, AnalysisResponse
from app.services.analysis_service import RealAnalysisService, MockAnalysisService
from app.services.base_analysis import BaseAnalysisService

router = APIRouter()

def get_analysis_service() -> BaseAnalysisService:
    if os.getenv("EMBEDDING_URL"):
        return RealAnalysisService()
    return MockAnalysisService()

@router.post("/send-petition", response_model=AnalysisResponse)
async def analyze_petition(
    petition: PetitionRequest, 
    service: BaseAnalysisService = Depends(get_analysis_service)
):
    try:
        return await service.process_petition(petition)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")