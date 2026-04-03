import httpx
import os
from datetime import datetime
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
                # TODO: Obter o last update pelo serviço de embedding
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
