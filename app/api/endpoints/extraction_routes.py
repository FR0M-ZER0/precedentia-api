from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.extraction_service import ExtractionService
from app.schemas.match_schema import MatchResponse
from app.repositories.search_repository import SearchRecord, search_repository

router = APIRouter()


@router.post("/extract", response_model=MatchResponse)
async def extract_pdf_data(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Por Favor, envie um arquivo PDF.")

    try:
        file_bytes = await file.read()

        petition_path = ExtractionService.save_pdf_locally(file_bytes, user_id)

        result = await ExtractionService.extract_text_from_pdf(file_bytes)

        structured_petition = await ExtractionService.send_petition_to_summary(
            result["text"]
        )

        precedents_response = await ExtractionService.send_to_embedding(
            structured_petition
        )

        precedent_ids = ExtractionService.extract_precedent_ids(precedents_response)

        record = SearchRecord(
            user_id=user_id,
            precedents=precedent_ids,
            petition_path=petition_path,
        )
        search_repository.save(record, db)

        return precedents_response

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar o arquivo: {str(e)}"
        )
