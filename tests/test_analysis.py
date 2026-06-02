# tests/test_analysis.py
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.api.endpoints.analysis_routes import get_analysis_service
from app.services.base_analysis import BaseAnalysisService


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


# ── Mock ──────────────────────────────────────────────────────────────────────


class MockAnalysisService(BaseAnalysisService):
    async def process_petition(self, data, **kwargs):
        return {
            "query": {
                "type": data.type,
                "facts": data.facts,
                "requests": " ".join(data.requests),
                "tribunal": data.tribunal,
            },
            "results": [
                {
                    "id": 1,
                    "name": "Precedente Teste",
                    "tribunal": "TJSP",
                    "situation": "Ativo",
                    "species": "Acórdão",
                    "summary": "Resumo do precedente.",
                    "question": "Questão jurídica.",
                    "url": "https://example.com",
                    "description": "Descrição do precedente.",
                    "last_update": "2024-01-01",
                    "applicability": "Aplicável",
                    "score": 0.95,
                }
            ],
            "total_found": 1,
        }


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def override_analysis_dependency():
    """Usa o mock por padrão em todos os testes."""
    app.dependency_overrides[get_analysis_service] = lambda: MockAnalysisService()
    yield
    app.dependency_overrides = {}


# ── Payload base reutilizável ─────────────────────────────────────────────────

VALID_PAYLOAD = {
    "user_id": 1,
    "type": "Indenizatória",
    "facts": "Erro no processamento bancário.",
    "requests": ["danos morais", "estorno"],
    "tribunal": "TJSP",
}


# ── Testes de sucesso ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_send_petition_success(client):
    response = await client.post("/analysis/send-petition", json=VALID_PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    assert "total_found" in data
    assert "results" in data
    assert "query" in data
    assert len(data["results"]) > 0


# ── Testes de campos obrigatórios ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_send_petition_missing_field_user_id(client):
    payload = {**VALID_PAYLOAD}
    del payload["user_id"]
    response = await client.post("/analysis/send-petition", json=payload)
    assert response.status_code == 422
    assert "user_id" in response.text


@pytest.mark.asyncio
async def test_send_petition_missing_field_type(client):
    payload = {**VALID_PAYLOAD}
    del payload["type"]
    response = await client.post("/analysis/send-petition", json=payload)
    assert response.status_code == 422
    assert "type" in response.text


@pytest.mark.asyncio
async def test_send_petition_missing_field_facts(client):
    payload = {**VALID_PAYLOAD}
    del payload["facts"]
    response = await client.post("/analysis/send-petition", json=payload)
    assert response.status_code == 422
    assert "facts" in response.text


@pytest.mark.asyncio
async def test_send_petition_missing_field_tribunal(client):
    payload = {**VALID_PAYLOAD}
    del payload["tribunal"]
    response = await client.post("/analysis/send-petition", json=payload)
    assert response.status_code == 422
    assert "tribunal" in response.text


@pytest.mark.asyncio
async def test_send_petition_missing_field_requests(client):
    payload = {**VALID_PAYLOAD}
    del payload["requests"]
    response = await client.post("/analysis/send-petition", json=payload)
    assert response.status_code == 422
    assert "requests" in response.text


# ── Testes de tipos inválidos ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_send_petition_invalid_type_as_dict(client):
    payload = {**VALID_PAYLOAD, "type": {"chave": "valor"}}
    response = await client.post("/analysis/send-petition", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_send_petition_invalid_requests_as_string(client):
    payload = {**VALID_PAYLOAD, "requests": "não é uma lista"}
    response = await client.post("/analysis/send-petition", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_send_petition_with_null_type(client):
    payload = {**VALID_PAYLOAD, "type": None}
    response = await client.post("/analysis/send-petition", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_send_petition_invalid_user_id_as_string(client):
    payload = {**VALID_PAYLOAD, "user_id": "não é um inteiro"}
    response = await client.post("/analysis/send-petition", json=payload)
    assert response.status_code == 422
