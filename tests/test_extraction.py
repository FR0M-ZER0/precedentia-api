import pytest
import pytest_asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from httpx import ASGITransport, AsyncClient
from app.main import app
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_TO_PDF = os.path.join(BASE_DIR, "fixtures", "teste2.pdf")

# ── Shared mock payloads ──────────────────────────────────────────────────────

MOCK_SUMMARY_RESPONSE = {
    "tipo": "trabalhista",
    "tribunal": "TRT",
    "fatos": "Fatos simulados para teste.",
    "pedidos": ["Pedido de indenização", "Pedido de verbas rescisórias"],
}

MOCK_EMBEDDING_RESPONSE = {
    "query": {
        "type": "trabalhista",
        "tribunal": "TRT",
        "facts": "Fatos simulados para teste.",
        "requests": "Pedido de indenização Pedido de verbas rescisórias",
    },
    "results": [
        {
            "id": "precedent:001",
            "name": "Precedente Simulado 1",
            "tribunal": "TRT",
            "situation": "Procedente",
            "description": "Descrição simulada do precedente 1.",
            "url": "http://example.com/precedent/001",
            "similarity_score": 0.95,
            "rerank_score": 0.90,
        },
        {
            "id": "precedent:002",
            "name": "Precedente Simulado 2",
            "tribunal": "TRT",
            "situation": "Parcialmente Procedente",
            "description": "Descrição simulada do precedente 2.",
            "url": "http://example.com/precedent/002",
            "similarity_score": 0.85,
            "rerank_score": 0.80,
        },
    ],
    "total_found": 2,
}


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


# ── Unit test: PDF text extraction (no external calls) ───────────────────────

@pytest.mark.asyncio
async def test_extraction_service_logic():
    from app.services.extraction_service import ExtractionService

    if not os.path.exists(PATH_TO_PDF):
        pytest.fail(f"Arquivo não encontrado em: {PATH_TO_PDF}")

    with open(PATH_TO_PDF, "rb") as f:
        pdf_content = f.read()

    result = await ExtractionService.extract_text_from_pdf(pdf_content)

    assert result is not None
    assert "text" in result
    assert "count" in result
    assert isinstance(result["text"], str)
    assert result["count"] > 0


# ── Integration test: full endpoint (external services mocked) ────────────────

@pytest.mark.asyncio
async def test_extract_pdf_endpoint_success(client):
    if not os.path.exists(PATH_TO_PDF):
        pytest.fail(f"Arquivo não encontrado em: {PATH_TO_PDF}")

    with (
        patch(
            "app.services.extraction_service.ExtractionService.send_petition_to_summary",
            new_callable=AsyncMock,
            return_value=MOCK_SUMMARY_RESPONSE,
        ),
        patch(
            "app.services.extraction_service.ExtractionService.send_to_embedding",
            new_callable=AsyncMock,
            return_value=MOCK_EMBEDDING_RESPONSE,
        ),
        patch(
            "app.repositories.petition_repository.petition_repository.save",
            return_value=MagicMock(),
        ),
    ):
        with open(PATH_TO_PDF, "rb") as f:
            response = await client.post(
                "/documents/extract",
                files={"file": ("teste2.pdf", f, "application/pdf")},
                data={"user_id": "1"},
            )

    assert response.status_code == 200

    data = response.json()
    assert "query" in data
    assert "results" in data
    assert "total_found" in data
    assert data["total_found"] == 2
    assert data["results"][0]["id"] == "precedent:001"


# ── Integration test: wrong file format ───────────────────────────────────────

@pytest.mark.asyncio
async def test_extract_pdf_endpoint_wrong_format(client):
    response = await client.post(
        "/documents/extract",
        files={"file": ("documento.txt", b"Ola mundo", "text/plain")},
        data={"user_id": "1"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Por Favor, envie um arquivo PDF."
