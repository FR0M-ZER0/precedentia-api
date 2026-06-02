import pytest
import uuid
from httpx import ASGITransport, AsyncClient
from app.main import app
from datetime import datetime, timedelta

from app.core.database import SessionLocal
from app.models.user_model import User

EMAIL_ORIGINAL = f"antigo_{uuid.uuid4().hex[:6]}@teste.com"
EMAIL_NOVO = f"novo_{uuid.uuid4().hex[:6]}@teste.com"
SENHA = "password123"


@pytest.fixture
async def client():
    """Fixture para o cliente assíncrono básico."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def auth_client(client):
    """Fixture que registra, loga e 'força' a validação do 2FA no banco."""
    await client.post(
        "/auth/register", json={"email": EMAIL_ORIGINAL, "password": SENHA}
    )
    await client.post("/auth/login", json={"email": EMAIL_ORIGINAL, "password": SENHA})

    db = SessionLocal()
    user = db.query(User).filter(User.email == EMAIL_ORIGINAL).first()
    if user:
        user.two_factor_code = "123456"
        user.two_factor_expires = datetime.utcnow() + timedelta(minutes=15)
        db.commit()
    db.close()

    response = await client.post(
        "/auth/verify", json={"email": EMAIL_ORIGINAL, "code": "123456"}
    )
    token = response.json().get("access_token")

    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest.mark.asyncio
async def test_request_email_update_success(auth_client):
    payload = {"new_email": EMAIL_NOVO}
    response = await auth_client.post("/auth/update-email/request", json=payload)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_confirm_email_update_success(auth_client):
    """Testa a etapa final de confirmação da troca de e-mail."""
    db = SessionLocal()
    user = db.query(User).filter(User.email == EMAIL_ORIGINAL).first()
    if user:
        user.two_factor_code = "123456"
        user.two_factor_expires = datetime.utcnow() + timedelta(minutes=15)
        db.commit()
    db.close()

    payload = {"new_email": EMAIL_NOVO, "code": "123456"}
    response = await auth_client.post("/auth/update-email/confirm", json=payload)

    assert response.status_code == 200
    assert response.json()["new_email"] == EMAIL_NOVO


@pytest.mark.asyncio
async def test_update_email_invalid_format(auth_client):
    payload = {"new_email": "email_invalido"}
    response = await auth_client.post("/auth/update-email/request", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_email_already_exists(auth_client, client):
    email_ocupado = "outro_usuario@teste.com"
    await client.post(
        "/auth/register", json={"email": email_ocupado, "password": SENHA}
    )

    payload = {"new_email": email_ocupado}
    response = await auth_client.post("/auth/update-email/request", json=payload)
    assert response.status_code == 400
