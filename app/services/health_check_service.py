from app.schemas.health_check_schema import HealthResponse
from datetime import datetime, timezone


class HealthCheckService:
    @staticmethod
    def check() -> HealthResponse:
        return HealthResponse(status="Ok", timestamp=datetime.now(timezone.utc))
