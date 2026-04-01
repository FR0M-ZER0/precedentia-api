import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.api.endpoints.analysis_routes import get_analysis_service
from app.services.analysis_service import MockAnalysisService


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture(autouse=True)
def override_analysis_dependency():
    app.dependency_overrides[get_analysis_service] = lambda: MockAnalysisService()
    yield
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_send_petition_success(client):
    payload = {
        "type": "Indenizatória",
        "facts": "Erro no processamento bancário.",
        "text": "Texto extraído da petição.",
        "requests": ["danos morais", "estorno"],
    }
    params = {"tribunals": ["TJSP"], "page": 1, "page_size": 10}

    response = await client.post("/analysis/send-petition", json=payload, params=params)

    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "precedents" in data
    assert len(data["precedents"]) > 0


@pytest.mark.asyncio
async def test_send_petition_missing_field_type(client):
    payload = {"facts": "fatos", "text": "texto", "requests": []}
    response = await client.post("/analysis/send-petition", json=payload)
    assert response.status_code == 422
    assert "type" in response.text


@pytest.mark.asyncio
async def test_send_petition_missing_field_facts(client):
    payload = {"type": "Ação", "text": "texto", "requests": []}
    response = await client.post("/analysis/send-petition", json=payload)
    assert response.status_code == 422
    assert "facts" in response.text


@pytest.mark.asyncio
async def test_send_petition_missing_field_text(client):
    payload = {"type": "Ação", "facts": "fatos", "requests": []}
    response = await client.post("/analysis/send-petition", json=payload)
    assert response.status_code == 422
    assert "text" in response.text


@pytest.mark.asyncio
async def test_send_petition_missing_field_requests(client):
    payload = {"type": "Ação", "facts": "fatos", "text": "texto"}
    response = await client.post("/analysis/send-petition", json=payload)
    assert response.status_code == 422
    assert "requests" in response.text


@pytest.mark.asyncio
async def test_send_petition_invalid_type_as_dict(client):
    payload = {
        "type": {"chave": "valor"},
        "facts": "fatos",
        "text": "texto",
        "requests": [],
    }
    response = await client.post("/analysis/send-petition", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_send_petition_invalid_list_as_string(client):
    payload = {
        "type": "Ação",
        "facts": "fatos",
        "text": "texto",
        "requests": "não é uma lista",
    }
    response = await client.post("/analysis/send-petition", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_send_petition_with_null_values(client):
    payload = {"type": None, "facts": "fatos", "text": "texto", "requests": []}
    response = await client.post("/analysis/send-petition", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_invalid_tribunal_literal_in_url(client):
    payload = {"type": "A", "facts": "B", "text": "C", "requests": []}
    params = {"tribunals": ["TJ-MARTE"]}
    response = await client.post("/analysis/send-petition", json=payload, params=params)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_pagination_out_of_bounds(client):
    payload = {"type": "A", "facts": "B", "text": "C", "requests": []}
    params = {"page_size": 500}
    response = await client.post("/analysis/send-petition", json=payload, params=params)
    assert response.status_code == 422
