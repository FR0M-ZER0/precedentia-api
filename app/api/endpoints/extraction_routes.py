# app/api/endpoints/extraction_routes.py

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.extraction_service import ExtractionService
from app.schemas.match_schema import MatchResponse
from app.repositories.petition_repository import PetitionRecord, petition_repository

router = APIRouter()


@router.post("/extract", response_model=MatchResponse)
async def extract_pdf_data(
    file: UploadFile = File(...),
    user_id: int = Form(...),
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Por Favor, envie um arquivo PDF.")

    try:
        file_bytes = await file.read()

        # 1. Save a copy of the PDF locally with a timestamped name
        petition_path = ExtractionService.save_pdf_locally(file_bytes, user_id)

        # 2. Extract text from the PDF
        result = await ExtractionService.extract_text_from_pdf(file_bytes)

        # 3. Summarise / deconstruct the petition
        structured_petition = await ExtractionService.send_petition_to_summary(result["text"])

        # 4. Find matching precedents
        precedents_response = await ExtractionService.send_to_embedding(structured_petition)

        # 5. Extract precedent IDs and persist path + precedents
        precedent_ids = ExtractionService.extract_precedent_ids(precedents_response)

        record = PetitionRecord(
            user_id=user_id,
            petition_path=petition_path,
            precedents=precedent_ids,
        )
        petition_repository.save(record)

        return precedents_response

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar o arquivo: {str(e)}"
        )
