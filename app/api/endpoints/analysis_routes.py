from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
import json
import os
from sqlalchemy.orm import Session
from app.api.endpoints.auth_routes import get_current_user
from app.models.search_model import Search
from app.schemas.petition_schema import PetitionRequest
from app.services.analysis_service import RealAnalysisService
from app.services.base_analysis import BaseAnalysisService
from app.core.database import get_db
from app.models.user_model import User
from app.repositories.search_repository import SearchRecord, search_repository
from app.schemas.search_schema import SearchResponse


router = APIRouter()


def get_analysis_service() -> BaseAnalysisService:
    return RealAnalysisService()


@router.post("/send-petition")
async def analyze_petition(
    petition: PetitionRequest,
    service: BaseAnalysisService = Depends(get_analysis_service),
    db: Session = Depends(get_db),
):
    async def event_stream():
        precedents_buffer = []

        try:
            async for event_name, payload in service.stream_petition(data=petition):
                if event_name == "precedent":
                    precedents_buffer.append(payload)

                yield f"event: {event_name}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"

                if event_name == "done":
                    try:
                        record = SearchRecord(
                            user_id=petition.user_id,
                            precedents=precedents_buffer,
                        )
                        record.type = petition.type
                        record.tribunal = petition.tribunal
                        record.facts = petition.facts
                        record.requests = " ".join(petition.requests)
                        search_repository.save(record, db)
                    except Exception as e:
                        print(f"Erro ao salvar no DB: {e}")

        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'message': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "X-Accel-Buffering": "no",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
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


@router.get("/searches", response_model=list[SearchResponse])
async def get_user_searches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    searches = db.query(Search).filter(Search.user_id == current_user.id).all()
    return searches


@router.get("/searches/{search_id}", response_model=SearchResponse)
async def get_search(
    search_id: int,
    db: Session = Depends(get_db),
):
    search = db.query(Search).filter(Search.id == search_id).first()

    if not search:
        raise HTTPException(status_code=404, detail="Pesquisa não encontrada.")

    return search
