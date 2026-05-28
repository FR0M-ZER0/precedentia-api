import json
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.sentence_service import SentenceService
from app.services.extraction_service import ExtractionService
from app.repositories.search_repository import SearchRecord, search_repository

router = APIRouter()


@router.post("/extract-process")
async def extract_process_data(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db),
):
    """
    Recebe um processo judicial completo em PDF (pode ter milhares de páginas),
    localiza e extrai apenas a petição inicial, e devolve os precedentes
    via Server-Sent Events
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400,
                            detail="Por favor, envie um arquivo PDF.")

    file_bytes = await file.read()

    try:
        petition_path = ExtractionService.save_pdf_locally(file_bytes, user_id)
        result = await SentenceService.extract_petition_text(file_bytes)
        structured_petition = await ExtractionService.send_petition_to_summary(
            result["text"]
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar o arquivo: {str(e)}"
        )

    async def event_stream():
        precedents_buffer = []

        try:
            async for event_name, payload in ExtractionService.stream_embedding(
                structured_petition
            ):
                if event_name == "precedent":
                    precedents_buffer.append(payload)

                yield f"event: {event_name}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"

                if event_name == "done":
                    try:
                        snapshot = ExtractionService.extract_precedents_snapshot(
                            {"results": precedents_buffer}
                        )
                        record = SearchRecord(
                            user_id=user_id,
                            precedents=snapshot,
                            petition_path=petition_path,
                        )
                        record.type = structured_petition.get("tipo")
                        record.tribunal = structured_petition.get("tribunal")
                        record.facts = structured_petition.get("fatos")
                        record.requests = " ".join(
                            structured_petition.get("pedidos", [])
                        )
                        search_repository.save(record, db)
                    except Exception as e:
                        print(f"Erro ao salvar no DB: {e}")

        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'message': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "X-Accel-Buffering": "no",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
