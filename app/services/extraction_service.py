import re
from pypdf import PdfReader
import io


class ExtractionService:
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
