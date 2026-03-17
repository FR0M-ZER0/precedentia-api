import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.api.endpoints.analysis_routes import get_analysis_service
from app.services.analysis_service import MockAnalysisService

@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
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
        "tribunal": "TJSP",
        "facts": "Ocorreu um erro no processamento bancário.",
        "requests": ["danos morais", "estorno"]
    }
    
    response = await client.post("/analysis/send-petition", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "suggested_precedents" in data
    assert len(data["suggested_precedents"]) > 0

@pytest.mark.asyncio
async def test_send_petition_missing_field(client):
    payload = {
        "type": "Indenizatória",
        "tribunal": "TJSP",
        "requests": ["danos morais"]
    }
    
    response = await client.post("/analysis/send-petition", json=payload)
    
    assert response.status_code == 422
    assert "facts" in response.text

@pytest.mark.asyncio
async def test_send_petition_missing_field_facts(client):
    payload = {
        "type": "Indenizatória",
        "tribunal": "TJSP",
        "requests": ["danos morais"]
    }
    
    response = await client.post("/analysis/send-petition", json=payload)
    
    assert response.status_code == 422
    assert "facts" in response.text

@pytest.mark.asyncio
async def test_send_petition_missing_field_tribunal(client):
    payload = {
        "type": "Indenizatória",
        "facts": "Fatos aqui...",
        "requests": ["danos morais"]
    }
    
    response = await client.post("/analysis/send-petition", json=payload)
    
    assert response.status_code == 422
    assert "tribunal" in response.text

@pytest.mark.asyncio
async def test_send_petition_missing_field_requests(client):
    payload = {
        "type": "Indenizatória",
        "tribunal": "TJSP",
        "facts": "Fatos aqui..."
    }
    
    response = await client.post("/analysis/send-petition", json=payload)
    
    assert response.status_code == 422
    assert "requests" in response.text

@pytest.mark.asyncio
async def test_send_petition_missing_field_type(client):
    payload = {
        "tribunal": "TJSP",
        "facts": "Fatos aqui...",
        "requests": ["danos morais"]
    }
    
    response = await client.post("/analysis/send-petition", json=payload)
    
    assert response.status_code == 422
    assert "type" in response.text

@pytest.mark.asyncio
async def test_send_petition_invalid_type_as_dict(client):
    payload = {
        "type": {"campo": "valor"}, 
        "tribunal": "TJSP",
        "facts": "Fatos...",
        "requests": ["pedido"]
    }
    response = await client.post("/analysis/send-petition", json=payload)
    assert response.status_code == 422
    assert "type" in response.text

@pytest.mark.asyncio
async def test_send_petition_invalid_tribunal_as_list(client):
    payload = {
        "type": "Indenizatória",
        "tribunal": ["Tribunal", "Incorreto"],
        "facts": "Fatos...",
        "requests": ["pedido"]
    }
    response = await client.post("/analysis/send-petition", json=payload)
    assert response.status_code == 422
    assert "tribunal" in response.text

@pytest.mark.asyncio
async def test_send_petition_invalid_requests_as_int(client):
    payload = {
        "type": "Indenizatória",
        "tribunal": "TJSP",
        "facts": "Fatos...",
        "requests": 123
    }
    response = await client.post("/analysis/send-petition", json=payload)
    assert response.status_code == 422
    assert "requests" in response.text

@pytest.mark.asyncio
async def test_send_petition_with_null_values(client):
    payload = {
        "type": None,
        "tribunal": "TJSP",
        "facts": "Fatos...",
        "requests": ["pedido"]
    }
    response = await client.post("/analysis/send-petition", json=payload)
    assert response.status_code == 422
    assert "type" in response.text

@pytest.mark.asyncio
async def test_send_petition_invalid_list(client):
    payload = {
        "type": "Indenizatória",
        "tribunal": "TJSP",
        "facts": "Fatos aqui...",
        "requests": "não é uma lista"
    }
    
    response = await client.post("/analysis/send-petition", json=payload)
    
    assert response.status_code == 422