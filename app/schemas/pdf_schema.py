from pydantic import BaseModel


class PDFExtractionResponse(BaseModel):
    filename: str
    text: str
    total_pages: int
