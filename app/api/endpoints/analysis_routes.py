from fastapi import APIRouter, Depends, HTTPException
from app.schemas.petition_schema import PetitionRequest, PetitionResponse
from app.services.analysis_service import RealAnalysisService
from app.services.base_analysis import BaseAnalysisService
from app.repositories.petition_repository import PetitionRecord, petition_repository

router = APIRouter()


def get_analysis_service() -> BaseAnalysisService:
    return RealAnalysisService()


@router.post("/send-petition", response_model=PetitionResponse)
async def analyze_petition(
    petition: PetitionRequest,
    service: BaseAnalysisService = Depends(get_analysis_service),
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
        record = PetitionRecord(
            user_id=petition.user_id,
            precedents=precedent_ids,
        )
        record.type = petition.type
        record.tribunal = petition.tribunal
        record.facts = petition.facts
        record.requests = " ".join(petition.requests)

        petition_repository.save(record)

        return response

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar a petição: {str(e)}"
        )
