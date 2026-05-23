import json
from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Any, Optional


class SearchResponse(BaseModel):
    id: int
    type: Optional[str]
    tribunal: Optional[str]
    facts: Optional[str]
    requests: Optional[str]
    precedents: Optional[list[dict[str, Any]]] = None
    petition_path: Optional[str]
    user_id: int
    created_at: datetime
    updated_at: datetime

    @field_validator("precedents", mode="before")
    @classmethod
    def parse_precedents(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

    class Config:
        from_attributes = True
