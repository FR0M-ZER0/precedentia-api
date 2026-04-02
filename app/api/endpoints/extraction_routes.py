from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.extraction_service import ExtractionService
from app.schemas.pdf_schema import PDFExtractionResponse

router = APIRouter()


@router.post("/extract", response_model=PDFExtractionResponse)
async def extract_pdf_data(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Por Favor, envie um arquivo PDF.")

    try:
        text = await file.read()
        result = await ExtractionService.extract_text_from_pdf(text)

        external_response = await ExtractionService.send_petition_to_summary(
            result["text"]
        )

        return PDFExtractionResponse(
            filename=file.filename,
            petition=external_response,
            total_pages=result["count"],
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar o arquivo: {str(e)}"
        )
