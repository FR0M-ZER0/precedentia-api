from pydantic import BaseModel

class PDFExtractionResponse(BaseModel):
    filename: str
    content: str
    total_pages: int