import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_TO_PDF = os.path.join(BASE_DIR, "fixtures", "teste2.pdf")


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_extraction_service_logic():
    from app.services.extraction_service import ExtractionService

    if not os.path.exists(PATH_TO_PDF):
        pytest.fail(f"Arquivo não encontrado em: {PATH_TO_PDF}")

    with open(PATH_TO_PDF, "rb") as f:
        pdf_content = f.read()

    result = await ExtractionService.extract_text_from_pdf(pdf_content)
    assert result is not None

@pytest.mark.asyncio
async def test_extract_pdf_endpoint_wrong_format(client):
    files = {"file": ("documento.txt", b"Ola mundo", "text/plain")}

    response = await client.post("/documents/extract", files=files)

    assert response.status_code == 400
    assert response.json()["detail"] == "Por Favor, envie um arquivo PDF."
