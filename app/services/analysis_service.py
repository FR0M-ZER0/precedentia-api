import httpx
import os

from app.services.base_analysis import BaseAnalysisService


class RealAnalysisService(BaseAnalysisService):
    async def process_petition(self, data, **kwargs):
        url = f"{os.getenv('EMBEDDING_URL')}/api/match"

        payload = {
            "type": data.type,
            "facts": data.facts,
            "requests": " ".join(data.requests),
        }

        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            raw = response.json()

        results = raw.get("results", [])

        return {
            "query": {
                "type": data.type,
                "facts": data.facts,
                "requests": " ".join(data.requests),
                "tribunal": data.tribunal,
            },
            "results": [
                {
                    "id": item["id"],
                    "name": item["name"],
                    "tribunal": item["tribunal"],
                    "situation": item["situation"],
                    "url": item["url"],
                    "description": item["description"],
                    "similarity_score": item.get("similarity_score", 0.0),
                    "rerank_score": item.get("rerank_score", 0.0),
                }
                for item in results
            ],
            "total_found": raw.get("total_found", len(results)),
        }
