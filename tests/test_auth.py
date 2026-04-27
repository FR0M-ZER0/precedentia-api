import pytest
import uuid
from httpx import ASGITransport, AsyncClient
from app.main import app

UNIQUE_EMAIL = f"test_{uuid.uuid4().hex[:6]}@teste.com"
PASSWORD = "password123"


@pytest.fixture
async def client():
    """Fixture para criar o cliente de teste assíncrono."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_register_user_success(client):
    payload = {"email": UNIQUE_EMAIL, "password": PASSWORD}
    response = await client.post("/auth/register", json=payload)

    assert response.status_code == 201
    assert "sucesso" in response.json()["message"]


@pytest.mark.asyncio
async def test_register_duplicate_user(client):
    payload = {"email": UNIQUE_EMAIL, "password": PASSWORD}
    response = await client.post("/auth/register", json=payload)

    assert response.status_code == 400
    assert "já está cadastrado" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_and_2fa_trigger(client):
    payload = {"email": UNIQUE_EMAIL, "password": PASSWORD}
    response = await client.post("/auth/login", json=payload)

    assert response.status_code == 200
    assert "Código de verificação enviado" in response.json()["message"]


@pytest.mark.asyncio
async def test_read_me_unauthorized(client):
    response = await client.get("/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_register_invalid_email(client):
    payload = {"email": "email_invalido", "password": "123"}
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_password_reset_request(client):
    payload = {"email": UNIQUE_EMAIL}
    response = await client.post("/auth/password-reset/request", json=payload)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_logout_endpoint(client):

    response = await client.post("/auth/logout")
    assert response.status_code == 401
