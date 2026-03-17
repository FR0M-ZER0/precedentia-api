import httpx
import os
import asyncio
from app.services.base_analysis import BaseAnalysisService
from app.schemas.petition_schema import PetitionRequest

class RealAnalysisService(BaseAnalysisService):
    async def process_petition(self, data: PetitionRequest):
        url = os.getenv("EMBEDDING_URL")
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data.model_dump(), timeout=60.0)
            response.raise_for_status()
            return response.json()

class MockAnalysisService(BaseAnalysisService):
    async def process_petition(self, data: PetitionRequest):
        await asyncio.sleep(1.0)
        return {
            "status": "success",
            "message": f"Simulação: Petição do tipo '{data.type}' processada com sucesso.",
            "suggested_precedents": [
                {
                    "title": f"Precedente sobre {data.requests[0] if data.requests else 'Geral'}",
                    "similarity_score": 0.92,
                    "link": "https://pje.jus.br/exemplo"
                }
            ]
        }