from pydantic import BaseModel
from typing import Dict, Any


class PDFExtractionResponse(BaseModel):
    filename: str
    petition: Dict[str, Any]
    total_pages: int
