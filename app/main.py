from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.core.database import engine, Base
from pathlib import Path

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    petitions_dir = Path(__file__).resolve().parent.parent / "petitions"
    petitions_dir.mkdir(exist_ok=True)

    yield  # App runs here

    # Shutdown (add any cleanup logic here if needed)


app = FastAPI(title="PrecedentIA API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
