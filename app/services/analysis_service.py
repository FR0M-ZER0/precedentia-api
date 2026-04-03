from typing import List
import httpx
import os
from app.schemas.petition_schema import PetitionRequest
from datetime import datetime, timedelta
from app.services.base_analysis import BaseAnalysisService


class RealAnalysisService(BaseAnalysisService):
    async def process_petition(
        self,
        data,
        tribunals=None,
        q=None,
        status=None,
        score_order="desc",
        date_order=None,
        page=1,
        page_size=10,
    ):
        url = f"{os.getenv('EMBEDDING_URL')}/api/match"

        payload = {
            "type": data.type,
            # "tribunal": data.tribunal,
            "facts": data.facts,
            "requests": " ".join(data.requests),
        }

        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            raw = response.json()

        results = raw.get("results", [])

        precedents = [
            {
                "name": item["name"],
                "tribunal": item["tribunal"],
                "last_update": datetime.now(),
                "situation": item["situation"],
                "url": item["url"],
                "description": item["description"],
                "score": item.get("score") or item.get("similarity_score", 0.0),
                "rerank_score": item.get("rerank_score"),
            }
            for item in results
        ]

        total = raw.get("total_found", len(precedents))

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "precedents": precedents,
        }


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
        page_size: int = 10,
    ):
        now = datetime.now()
        all_data = [
            {
                "name": "Caso Alimentos A",
                "tribunal": "TJSP",
                "last_update": now - timedelta(days=2),
                "situation": "concluido",
                "url": "http://..",
                "description": "Pensao alimenticia...",
                "score": 0.95,
            },
            {
                "name": "Caso Danos B",
                "tribunal": "TRF3",
                "last_update": now - timedelta(days=10),
                "situation": "em andamento",
                "url": "http://..",
                "description": "Danos morais...",
                "score": 0.88,
            },
            {
                "name": "Revisional de Contrato C",
                "tribunal": "TJSP",
                "last_update": now - timedelta(hours=5),
                "situation": "concluido",
                "url": "http://..",
                "description": "Juros abusivos...",
                "score": 0.75,
            },
            {
                "name": "Indenização D",
                "tribunal": "STJ",
                "last_update": now - timedelta(days=1),
                "situation": "arquivado",
                "url": "http://..",
                "description": "Recurso especial...",
                "score": 0.92,
            },
            {
                "name": "Pensão por Morte E",
                "tribunal": "TRF3",
                "last_update": now - timedelta(minutes=30),
                "situation": "em andamento",
                "url": "http://..",
                "description": "Previdenciário...",
                "score": 0.81,
            },
        ]

        if q:
            all_data = [p for p in all_data if q.lower() in p["name"].lower()]

        if status:
            all_data = [p for p in all_data if p["situation"].lower() == status.lower()]

        if tribunals:
            all_data = [p for p in all_data if p["tribunal"] in tribunals]

        if date_order:
            all_data.sort(
                key=lambda x: x["last_update"], reverse=(date_order == "desc")
            )

        if score_order:
            all_data.sort(key=lambda x: x["score"], reverse=(score_order == "desc"))

        start = (page - 1) * page_size
        end = start + page_size
        paginated_data = all_data[start:end]

        return {
            "total": len(all_data),
            "page": page,
            "page_size": page_size,
            "precedents": paginated_data,
        }
