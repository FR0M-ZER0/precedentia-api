from fastapi import APIRouter, Depends, HTTPException

import os
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api.endpoints.auth_routes import get_current_user
from app.models.search_model import Search
from app.schemas.petition_schema import PetitionRequest, PetitionResponse
from app.services.analysis_service import RealAnalysisService
from app.services.base_analysis import BaseAnalysisService
from app.core.database import get_db
from app.models.user_model import User
from app.repositories.search_repository import SearchRecord, search_repository


router = APIRouter()


def get_analysis_service() -> BaseAnalysisService:
    return RealAnalysisService()


@router.post("/send-petition", response_model=PetitionResponse)
async def analyze_petition(
    petition: PetitionRequest,
    service: BaseAnalysisService = Depends(get_analysis_service),
    db: Session = Depends(get_db),
):
    try:
        # 1. Busca os precedentes no serviço de embedding
        response = await service.process_petition(data=petition)

        # 2. Extrai os IDs dos precedentes retornados
        precedent_ids = [
            str(result["id"])
            for result in response.get("results", [])
            if result.get("id") is not None
        ]

        # 3. Persiste os dados da petição + precedentes encontrados
        record = SearchRecord(
            user_id=petition.user_id,
            precedents=precedent_ids,
        )
        record.type = petition.type
        record.tribunal = petition.tribunal
        record.facts = petition.facts
        record.requests = " ".join(petition.requests)

        search_repository.save(record, db)

        return response

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar a petição: {str(e)}"
        )


@router.get("/download-pdf/{petition_id}")
async def download_petition_pdf(
    petition_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    petition = (
        db.query(Search)
        .filter(Search.id == petition_id, Search.user_id == current_user.id)
        .first()
    )

    if not petition or not petition.petition_path:
        raise HTTPException(
            status_code=404, detail="Ficheiro não encontrado ou acesso negado."
        )

    if not os.path.exists(petition.petition_path):
        raise HTTPException(
            status_code=404, detail="O ficheiro físico não foi encontrado no servidor."
        )

    return FileResponse(
        path=petition.petition_path,
        media_type="application/pdf",
        filename=f"peticao_{petition_id}.pdf",
    )
