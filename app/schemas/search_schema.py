from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SearchResponse(BaseModel):
    id: int
    type: Optional[str]
    tribunal: Optional[str]
    facts: Optional[str]
    requests: Optional[str]
    precedents: Optional[str]
    petition_path: Optional[str]
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
