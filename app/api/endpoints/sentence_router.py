import json
import httpx
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session
from markdown import markdown
from weasyprint import HTML
from app.core.database import get_db
from app.repositories.sentence_repository import sentence_repository
from app.services.sentence_service import SentenceService
from app.services.extraction_service import ExtractionService
from app.repositories.search_repository import SearchRecord, search_repository
from app.schemas.sentence_schema import GenerateSentenceRequest, EditSentenceRequest

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
        raise HTTPException(status_code=400, detail="Por favor, envie um arquivo PDF.")

    file_bytes = await file.read()

    try:
        petition_path = ExtractionService.save_pdf_locally(file_bytes, user_id)
        result = await SentenceService.extract_petition_text(file_bytes)
        structured_petition = await SentenceService.send_petition_to_summary(
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

        yield f"event: process_data\ndata: {json.dumps(structured_petition, ensure_ascii=False)}\n\n"

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


@router.post("/generate")
async def gerar_sentenca(body: GenerateSentenceRequest, db: Session = Depends(get_db)):
    try:
        payload = body.model_dump(exclude={"user_id"})
        result = await SentenceService.generate_sentence(payload)
        content = result.get("content")

        sentence = sentence_repository.save(
            content=content, user_id=body.user_id, db=db
        )

        return {"id": sentence.id, "content": content}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar sentença: {str(e)}")


@router.post("/edit")
async def editar_sentenca(body: EditSentenceRequest, db: Session = Depends(get_db)):
    if not body.change.strip():
        raise HTTPException(status_code=400, detail="Campo 'change' é obrigatório.")
    if not body.content.strip():
        raise HTTPException(status_code=400, detail="Campo 'content' é obrigatório.")

    try:
        result = await SentenceService.edit_sentence(body.content, body.change)
        updated_content = result.get("content")

        updated = sentence_repository.update_content_by_id(body.sentence_id, updated_content, db)

        return {"id": updated.id, "content": updated_content}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao editar sentença: {str(e)}")


@router.get("/{sentence_id}/pdf")
async def baixar_sentenca_pdf(sentence_id: int, db: Session = Depends(get_db)):
    sentence = sentence_repository.get_by_id(sentence_id, db)
    if not sentence:
        raise HTTPException(status_code=404, detail="Sentença não encontrada.")

    try:
        html_content = markdown(sentence.content)

        html_styled = f"""
        <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{
                        font-family: 'Times New Roman', serif;
                        font-size: 12pt;
                        line-height: 1.8;
                        margin: 3cm 2.5cm;
                        color: #000;
                        text-align: justify;
                    }}
                    h1, h2, h3 {{
                        text-align: center;
                        font-size: 12pt;
                        text-transform: uppercase;
                    }}
                    p {{ margin-bottom: 0.8em; }}
                </style>
            </head>
            <body>{html_content}</body>
        </html>
        """

        pdf_bytes = HTML(string=html_styled).write_pdf()

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=sentenca_{sentence_id}.pdf"
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar PDF: {str(e)}")
