from typing import List
import httpx
import os
from app.schemas.petition_schema import PetitionRequest
from datetime import datetime, timedelta
from app.services.base_analysis import BaseAnalysisService

class RealAnalysisService(BaseAnalysisService):
    async def process_petition(
        self, 
        data: PetitionRequest, 
        tribunals: list = None,
        q: str = None,
        status: str = None,
        score_order: str = "desc",
        date_order: str = None,
        page: int = 1,
        page_size: int = 10
    ):
        url = os.getenv("EMBEDDING_URL")
        
        params = {
            "tribunals": tribunals,
            "q": q,
            "status": status,
            "score_order": score_order,
            "date_order": date_order,
            "page": page,
            "page_size": page_size
        }
        
        params = {k: v for k, v in params.items() if v is not None}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url, 
                json=data.model_dump(), 
                params=params, 
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()

class MockAnalysisService(BaseAnalysisService):
    async def process_petition(
        self, 
        data: PetitionRequest,
        tribunals: List[str] = None,
        q: str = None, 
        status: str = None, 
        score_order="desc", 
        date_order=None, 
        page: int = 1, 
        page_size: int = 10
    ):
        now = datetime.now()
        all_data = [
            {"name": "Caso Alimentos A", "tribunal": "TJSP", "last_update": now - timedelta(days=2), "situation": "concluido", "url": "http://..", "description": "Pensao alimenticia...", "score": 0.95},
            {"name": "Caso Danos B", "tribunal": "TRF3", "last_update": now - timedelta(days=10), "situation": "em andamento", "url": "http://..", "description": "Danos morais...", "score": 0.88},
            {"name": "Revisional de Contrato C", "tribunal": "TJSP", "last_update": now - timedelta(hours=5), "situation": "concluido", "url": "http://..", "description": "Juros abusivos...", "score": 0.75},
            {"name": "Indenização D", "tribunal": "STJ", "last_update": now - timedelta(days=1), "situation": "arquivado", "url": "http://..", "description": "Recurso especial...", "score": 0.92},
            {"name": "Pensão por Morte E", "tribunal": "TRF3", "last_update": now - timedelta(minutes=30), "situation": "em andamento", "url": "http://..", "description": "Previdenciário...", "score": 0.81},
        ]

        if q:
            all_data = [p for p in all_data if q.lower() in p["name"].lower()]

        if status:
            all_data = [p for p in all_data if p["situation"].lower() == status.lower()]

        if tribunals:
            all_data = [p for p in all_data if p["tribunal"] in tribunals]

        if date_order:
            all_data.sort(
                key=lambda x: x["last_update"], 
                reverse=(date_order == "desc")
            )

        if score_order:
            all_data.sort(
                key=lambda x: x["score"], 
                reverse=(score_order == "desc")
            )

        start = (page - 1) * page_size
        end = start + page_size
        paginated_data = all_data[start:end]

        return {
            "total": len(all_data),
            "page": page,
            "page_size": page_size,
            "precedents": paginated_data
        }