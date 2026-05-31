import json
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
    precedents: str = Form(...),  # JSON string: '[{"name": "...", "question": "...", "description": "..."}]'
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        parsed_precedents = json.loads(precedents)

        extracted_texts = []
        for file in files:
            if file.content_type == "application/pdf":
                content_bytes = await file.read()
                extracted = await ExtractionService.extract_text_from_pdf(content_bytes)
                if "text" in extracted:
                    extracted_texts.append(extracted["text"])

        full_facts = facts_summary + "\n" + "\n".join(extracted_texts)

        generated_content = (
            f"PETIÇÃO INICIAL GERADA AUTOMATICAMENTE\n\n"
            f"Autor: {author_description}\n"
            f"Réu: {defendant_description}\n"
            f"Tipo de ação: {action_type}\n"
            f"Tribunal: {tribunal}\n"
            f"Fatos: {full_facts}\n"
            f"Pedidos: {requests}\n"
            f"Valor da causa: {value_of_cause}\n"
            f"Tutela urgente: {'Sim' if urgent_relief else 'Não'}\n"
            f"Justiça gratuita: {'Sim' if free_justice else 'Não'}\n"
            f"Precedentes: {json.dumps(parsed_precedents, ensure_ascii=False)}"
        )

        new_petition = Petition(
            content=generated_content,
            user_id=current_user.id,
        )
        db.add(new_petition)
        db.commit()
        db.refresh(new_petition)

        return new_petition

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Erro na geração da petição: {str(e)}"
        )


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
        raise HTTPException(
            status_code=404, detail="Petição não encontrada ou acesso negado."
        )

    try:
        edited_content = (
            f"{payload.content}\n\n"
            f"{payload.change}"
        )

        petition.content = edited_content
        db.commit()
        db.refresh(petition)

        return petition

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Erro ao editar a petição: {str(e)}"
        )


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
            line = (
                line
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
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