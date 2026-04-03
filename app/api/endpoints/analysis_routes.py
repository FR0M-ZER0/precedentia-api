from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.schemas.petition_schema import (
    TRIBUNAIS_VALIDOS,
    PaginatedPrecedentsResponse,
    PetitionRequest,
)
from app.services.analysis_service import RealAnalysisService
from app.services.base_analysis import BaseAnalysisService

router = APIRouter()


def get_analysis_service() -> BaseAnalysisService:
    return RealAnalysisService()


@router.post("/send-petition", response_model=PaginatedPrecedentsResponse)
async def analyze_petition(
    petition: PetitionRequest,
    tribunals: Optional[List[TRIBUNAIS_VALIDOS]] = Query(
        None, description="Filtrar por um ou mais tribunais"
    ),
    q: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    score_order: Optional[str] = Query("desc"),
    date_order: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
    service: BaseAnalysisService = Depends(get_analysis_service),
):
    return await service.process_petition(
        data=petition,
        tribunals=tribunals,
        q=q,
        status=status,
        score_order=score_order,
        date_order=date_order,
        page=page,
        page_size=page_size,
    )
