from fastapi import APIRouter
from app.schemas.health_check_schema import HealthResponse
from app.services.health_check_service import HealthCheckService


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check():
    return HealthCheckService.check()
