from fastapi import APIRouter
from app.api.endpoints.health_check_routes import router as health_router
from app.api.endpoints import auth_routes, extraction_routes, analysis_routes, generation_routes


api_router = APIRouter()

routers = [health_router]

for router in routers:
    api_router.include_router(router, prefix="/api")
    api_router.include_router(
        extraction_routes.router, prefix="/documents", tags=["extraction"]
    )
    api_router.include_router(
        analysis_routes.router, prefix="/analysis", tags=["analysis"]
    )
    api_router.include_router(
        auth_routes.router, prefix="/auth", tags=["Authentication"]
    )
    api_router.include_router(
        generation_routes.router, prefix="/generation", tags=["Generation"]
    )
