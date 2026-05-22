import pytest
import os
import uuid
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.core.database import SessionLocal
from app.models.user_model import User
from app.models.petition_model import Petition
from datetime import datetime, timedelta

TEST_EMAIL = f"juridico_{uuid.uuid4().hex[:6]}@fatec.sp.gov.br"
PASSWORD = "password123"
MOCK_PDF_DIR = "app/documents/petitions"
MOCK_PDF_PATH = f"{MOCK_PDF_DIR}/test_document.pdf"


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def auth_client(client):
    """Retorna um cliente autenticado e garante que o arquivo de teste existe."""
    os.makedirs(MOCK_PDF_DIR, exist_ok=True)
    with open(MOCK_PDF_PATH, "wb") as f:
        f.write(b"%PDF-1.4 mock content")

    await client.post(
        "/auth/register", json={"email": TEST_EMAIL, "password": PASSWORD}
    )
    await client.post("/auth/login", json={"email": TEST_EMAIL, "password": PASSWORD})

    db = SessionLocal()
    user = db.query(User).filter(User.email == TEST_EMAIL).first()
    user.two_factor_code = "123456"
    user.two_factor_expires = datetime.utcnow() + timedelta(minutes=10)
    db.commit()
    user_id = user.id
    db.close()

    response = await client.post(
        "/auth/verify", json={"email": TEST_EMAIL, "code": "123456"}
    )
    token = response.json().get("access_token")
    client.headers.update({"Authorization": f"Bearer {token}"})

    client.user_id = user_id
    return client


@pytest.mark.asyncio
async def test_download_pdf_success(auth_client):
    """Testa o download bem-sucedido de uma petição criada no banco pelo teste."""
    db = SessionLocal()
    mock_petition = Petition(
        type="Ação de Teste",
        tribunal="TJSP",
        facts="Fatos de teste",
        requests="Pedidos de teste",
        file_path=MOCK_PDF_PATH,
        user_id=auth_client.user_id,
    )
    db.add(mock_petition)
    db.commit()
    petition_id = mock_petition.id
    db.close()

    response = await auth_client.get(f"/analysis/download-pdf/{petition_id}")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"


async def test_download_pdf_forbidden(auth_client, client):
    db = SessionLocal()
    random_email = f"hacker_{uuid.uuid4().hex[:6]}@teste.com"
    outro_user = User(email=random_email, password="...")
    db.add(outro_user)
    db.commit()

    pet_proibida = Petition(
        type="Privado",
        tribunal="STF",
        facts="...",
        requests="...",
        file_path=MOCK_PDF_PATH,
        user_id=outro_user.id,
    )
    db.add(pet_proibida)
    db.commit()
    id_proibido = pet_proibida.id
    db.close()

    response = await auth_client.get(f"/analysis/download-pdf/{id_proibido}")

    assert response.status_code in [403, 404]


@pytest.mark.asyncio
async def test_download_pdf_not_found(auth_client):
    """Testa erro 404 para ID que não existe no banco."""
    response = await auth_client.get("/analysis/download-pdf/999999")
    assert response.status_code == 404
