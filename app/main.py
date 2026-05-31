from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.api.router import api_router
from app.core.database import engine, Base
from pathlib import Path

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    petitions_dir = Path(__file__).resolve().parent.parent / "petitions"
    petitions_dir.mkdir(exist_ok=True)
    yield


app = FastAPI(title="PrecedentIA API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
        openapi_version="3.0.3",
    )

    for path_data in schema.get("paths", {}).values():
        for operation in path_data.values():
            body = operation.get("requestBody", {})
            content = body.get("content", {})
            multipart = content.get("multipart/form-data", {})
            ref = multipart.get("schema", {}).get("$ref", "")
            if not ref:
                continue
            schema_name = ref.split("/")[-1]
            component = schema.get("components", {}).get("schemas", {}).get(schema_name, {})
            for prop_name, prop in component.get("properties", {}).items():
                if prop.get("contentMediaType"):
                    prop.pop("contentMediaType", None)
                    prop["format"] = "binary"
                if prop.get("type") == "array":
                    items = prop.get("items", {})
                    if items.get("contentMediaType"):
                        items.pop("contentMediaType", None)
                        items["format"] = "binary"

    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi