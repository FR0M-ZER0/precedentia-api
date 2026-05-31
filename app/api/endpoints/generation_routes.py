import json
import httpx
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user_model import User
from app.models.petition_model import Petition
from app.api.endpoints.auth_routes import get_current_user
from app.schemas.generation_schema import PetitionResponse, PetitionEditRequest
from app.services.extraction_service import ExtractionService

router = APIRouter(prefix="/petitions", tags=["Generation"])

SUMMARY_URL = os.getenv("SUMMARY_URL")


@router.post("/generate", response_model=PetitionResponse)
async def generate_initial_petition(
    author_description: str = Form(...),
    defendant_description: str = Form(...),
    action_type: str = Form(...),
    tribunal: str = Form(...),
    facts_summary: str = Form(...),
    requests: str = Form(...),
    value_of_cause: str = Form(...),
    urgent_relief: bool = Form(...),
    free_justice: bool = Form(...),
    precedents: str = Form(...),
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        parsed_precedents = json.loads(precedents)
        parsed_requests = json.loads(requests) if requests.strip().startswith("[") else [r.strip() for r in requests.split(",")]

        extracted_texts = []
        for file in files:
            if file.content_type == "application/pdf":
                content_bytes = await file.read()
                extracted = await ExtractionService.extract_text_from_pdf(content_bytes)
                if "text" in extracted:
                    extracted_texts.append(extracted["text"])

        payload = {
            "author_description": author_description,
            "defendant_description": defendant_description,
            "action_type": action_type,
            "tribunal": tribunal,
            "facts_summary": facts_summary,
            "files": extracted_texts,
            "requests": parsed_requests,
            "cause_value": value_of_cause,
            "urgent_injunction": urgent_relief,
            "free_justice": free_justice,
            "precedents": parsed_precedents,
        }

        async with httpx.AsyncClient(timeout=1000.0) as client:
            response = await client.post(f"{SUMMARY_URL}/api/petition/generate", json=payload)

        response.raise_for_status()
        generated_content = response.json().get("content")
        generated_content = generated_content.strip()
        if generated_content.startswith("```"):
            generated_content = generated_content.split("\n", 1)[-1]
        if generated_content.endswith("```"):
            generated_content = generated_content.rsplit("\n", 1)[0]
        generated_content = generated_content.strip()

        new_petition = Petition(
            content=generated_content,
            user_id=current_user.id,
        )
        db.add(new_petition)
        db.commit()
        db.refresh(new_petition)

        return new_petition

    except httpx.HTTPStatusError as e:
        db.rollback()
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro na geração da petição: {str(e)}")


@router.post("/edit", response_model=PetitionResponse)
async def edit_petition_content(
    payload: PetitionEditRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    petition = (
        db.query(Petition)
        .filter(Petition.id == payload.id, Petition.user_id == current_user.id)
        .first()
    )
    if not petition:
        raise HTTPException(status_code=404, detail="Petição não encontrada ou acesso negado.")

    if not payload.change.strip():
        raise HTTPException(status_code=400, detail="Campo 'change' é obrigatório.")
    if not payload.content.strip():
        raise HTTPException(status_code=400, detail="Campo 'content' é obrigatório.")

    try:
        async with httpx.AsyncClient(timeout=1000.0) as client:
            response = await client.post(
                f"{SUMMARY_URL}/api/petition/edit",
                json={"content": payload.content, "change": payload.change},
            )

        response.raise_for_status()
        updated_content = response.json().get("content")

        updated_content = updated_content.strip()
        if updated_content.startswith("```"):
            updated_content = updated_content.split("\n", 1)[-1]
        if updated_content.endswith("```"):
            updated_content = updated_content.rsplit("\n", 1)[0]
        updated_content = updated_content.strip()

        petition.content = updated_content
        db.commit()
        db.refresh(petition)

        return petition

    except httpx.HTTPStatusError as e:
        db.rollback()
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao editar a petição: {str(e)}")


@router.get("/{id}/pdf")
async def export_petition_to_pdf(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    petition = (
        db.query(Petition)
        .filter(Petition.id == id, Petition.user_id == current_user.id)
        .first()
    )
    if not petition:
        raise HTTPException(status_code=404, detail="Petição não encontrada.")

    try:
        import os
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

        os.makedirs("app/documents/generated", exist_ok=True)
        pdf_path = f"app/documents/generated/petition_{id}.pdf"

        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=3 * cm,
            leftMargin=3 * cm,
            topMargin=3 * cm,
            bottomMargin=2 * cm,
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "TitleStyle",
            parent=styles["Title"],
            fontSize=14,
            spaceAfter=20,
            alignment=1,
        )

        body_style = ParagraphStyle(
            "BodyStyle",
            parent=styles["Normal"],
            fontSize=12,
            leading=18,
            spaceAfter=10,
            alignment=4,
        )

        story = []
        story.append(Paragraph("PETIÇÃO INICIAL", title_style))
        story.append(Spacer(1, 0.5 * cm))

        for line in petition.content.split("\n"):
            line = line.strip()
            if not line:
                story.append(Spacer(1, 0.3 * cm))
                continue
            line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(line, body_style))

        doc.build(story)

        return FileResponse(
            path=pdf_path,
            filename=f"peticao_{id}.pdf",
            media_type="application/pdf",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao gerar arquivo PDF: {str(e)}"
        )
