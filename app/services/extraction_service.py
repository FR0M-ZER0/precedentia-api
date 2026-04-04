import os
import re
import httpx
from pypdf import PdfReader
import io
from dotenv import load_dotenv

load_dotenv()


class ExtractionService:
    @staticmethod
    async def send_petition_to_summary(text: str):
        url = f"{os.getenv('SUMMARY_URL')}/api/deconstruct"

        payload = {"peticao": text}

        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(url, json=payload)

        response.raise_for_status()
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

        async with httpx.AsyncClient(timeout=180.0) as client:
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
                if text:
                    clean_page = text.replace("\n", " ").replace("\r", " ")
                    clean_page = re.sub(r"\s+", " ", clean_page)
                    full_text += clean_page + " "

        return {"text": full_text.strip(), "count": len(pages)}
