from fastapi import APIRouter, Depends, HTTPException
import os
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api.endpoints.auth_routes import get_current_user
from app.models.petition_model import Petition
from app.models.petition_model import Petition
from app.schemas.petition_schema import PetitionRequest, PetitionResponse
from app.services.analysis_service import RealAnalysisService
from app.services.base_analysis import BaseAnalysisService
from app.core.database import get_db
from app.api.endpoints.auth_routes import get_current_user
from app.models.user_model import User
from app.models.petition_model import Petition

router = APIRouter()


def get_analysis_service() -> BaseAnalysisService:
    return RealAnalysisService()


@router.post("/send-petition", response_model=PetitionResponse)
async def analyze_petition(
    petition: PetitionRequest,
    service: BaseAnalysisService = Depends(get_analysis_service),
):
    return await service.process_petition(data=petition)

@router.get("/download-pdf/{petition_id}")
async def download_petition_pdf(
    petition_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    petition = db.query(Petition).filter(
        Petition.id == petition_id, 
        Petition.user_id == current_user.id
    ).first()

    if not petition or not petition.file_path:
        raise HTTPException(status_code=404, detail="Ficheiro não encontrado ou acesso negado.")

    if not os.path.exists(petition.file_path):
        raise HTTPException(status_code=404, detail="O ficheiro físico não foi encontrado no servidor.")

    return FileResponse(
        path=petition.file_path,
        media_type='application/pdf',
        filename=f"peticao_{petition_id}.pdf"
    )