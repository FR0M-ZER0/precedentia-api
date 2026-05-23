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
    async def send_to_embedding(data: dict):
        url = f"{os.getenv('EMBEDDING_URL')}/api/match"
        payload = {
            "type": data.get("tipo"),
            "tribunal": data.get("tribunal"),
            "facts": data.get("fatos"),
            "requests": " ".join(data.get("pedidos", [])),
        }

        async with httpx.AsyncClient(timeout=1000.0) as client:
            response = await client.post(url, json=payload)

        response.raise_for_status()
        return response.json()

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
