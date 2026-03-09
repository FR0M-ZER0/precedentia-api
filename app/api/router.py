from fastapi import APIRouter
from app.api.endpoints.health_check_routes import router as health_router

api_router = APIRouter()

routers = [health_router]

for router in routers:
    api_router.include_router(router, prefix="/api")
