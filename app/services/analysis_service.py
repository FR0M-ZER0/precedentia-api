import httpx
import json
import os

from app.services.base_analysis import BaseAnalysisService


class RealAnalysisService(BaseAnalysisService):
    async def stream_petition(self, data, **kwargs):
        url = f"{os.getenv('EMBEDDING_URL')}/api/match/stream"

        payload = {
            "type": data.type,
            "tribunal": data.tribunal,
            "facts": data.facts,
            "requests": " ".join(data.requests),
        }

        event_name = "message"

        async with httpx.AsyncClient(timeout=180.0) as client:
            async with client.stream("POST", url, json=payload) as response:
                response.raise_for_status()

                async for raw_line in response.aiter_lines():
                    line = raw_line.strip()

                    if not line or line.startswith(":"):
                        continue

                    if line.startswith("event:"):
                        event_name = line.removeprefix("event:").strip()
                        continue

                    if line.startswith("data:"):
                        raw_data = line.removeprefix("data:").strip()
                        try:
                            payload_data = json.loads(raw_data)
                        except json.JSONDecodeError:
                            continue

                        yield event_name, payload_data
                        event_name = "message"

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
                    "species": item["species"],
                    "summary": item["summary"],
                    "question": item["question"],
                    "situation": item["situation"],
                    "last_update": item["last_update"],
                    "url": item["url"],
                    "description": item["description"],
                    "score": item.get("score", 0.0),
                    "applicability": item.get("applicability"),
                }
                for item in results
            ],
            "total_found": raw.get("total_found", len(results)),
        }


class MockAnalysisService:
    async def process_petition(self, data):
        reqs = getattr(data, "requests", [])
        reqs_str = " ".join(reqs) if isinstance(reqs, list) else str(reqs)

        return {
            "query": {
                "type": getattr(data, "type", "Indenizatória"),
                "facts": getattr(data, "facts", "Fatos simulados"),
                "requests": reqs_str,
                "tribunal": getattr(data, "tribunal", "TJSP"),
            },
            "total_found": 1,
            "results": [
                {
                    "id": 1,
                    "name": "Precedente de Teste (Mock)",
                    "tribunal": "TJSP",
                    "situation": "Julgado",
                    "species": "Apelação",
                    "summary": "Resumo simulado.",
                    "question": "Questão jurídica simulada.",
                    "url": "https://exemplo.com/doc.pdf",
                    "description": "Este é um resultado simulado completo para o teste.",
                    "last_update": "2024-01-01",
                    "applicability": "Alta",
                    "score": 0.95,
                }
            ],
        }
