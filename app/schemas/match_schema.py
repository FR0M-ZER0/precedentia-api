from pydantic import BaseModel
from typing import List, Dict, Any


class MatchResponse(BaseModel):
    query: Dict[str, Any]
    results: List[Dict[str, Any]]
    total_found: int
