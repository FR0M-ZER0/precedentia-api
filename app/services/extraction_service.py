import json
import os
import re
import httpx
from pypdf import PdfReader
import io
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

_PETITIONS_DIR = Path(__file__).resolve().parent.parent.parent / "petitions"


class ExtractionService:
    @staticmethod
    def save_pdf_locally(file_bytes: bytes, user_id: int) -> str:
        """
        Saves the PDF to the petitions/ folder with a datetime-stamped name.
        Returns the file path as a string.
        """
        _PETITIONS_DIR.mkdir(exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"petition_{user_id}_{timestamp}.pdf"
        file_path = _PETITIONS_DIR / filename

        with open(file_path, "wb") as f:
            f.write(file_bytes)

        return str(file_path)

    @staticmethod
    def extract_precedents_snapshot(match_response: dict) -> list[dict]:
        return [
            {
                "id": result["id"],
                "name": result["name"],
                "tribunal": result["tribunal"],
                "species": result["species"],
                "summary": result["summary"],
                "question": result["question"],
                "situation": result["situation"],
                "last_update": result["last_update"],
                "url": result["url"],
                "description": result["description"],
                "score": result.get("score", 0.0),
                "applicability": result.get("applicability"),
            }
            for result in match_response.get("results", [])
            if result.get("id") is not None
        ]

    @staticmethod
    async def send_petition_to_summary(text: str):
        url = f"{os.getenv('SUMMARY_URL')}/api/deconstruct"
        payload = {"peticao": text}

        async with httpx.AsyncClient(timeout=1000.0) as client:
            response = await client.post(url, json=payload)

        response.raise_for_status()
        print(response.json())
        return response.json()

    @staticmethod
    async def stream_embedding(data: dict):
        url = f"{os.getenv('EMBEDDING_URL')}/api/match/stream"
        payload = {
            "type": data.get("tipo"),
            "tribunal": data.get("tribunal"),
            "facts": data.get("fatos"),
            "requests": " ".join(data.get("pedidos", [])),
        }

        event_name = "message"

        async with httpx.AsyncClient(timeout=1000.0) as client:
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

    @staticmethod
    async def extract_text_from_pdf(file_bytes: bytes) -> dict:
        pdf_file = io.BytesIO(file_bytes)
        reader = PdfReader(pdf_file)
        pages = reader.pages
        full_text = ""

        for page in pages:
            text = page.extract_text()
            if text:
                clean_page = text.replace("\n", " ").replace("\r", " ")
                clean_page = re.sub(r"\s+", " ", clean_page)
                full_text += clean_page + " "

        print(full_text.strip())
        return {"text": full_text.strip(), "count": len(pages)}
