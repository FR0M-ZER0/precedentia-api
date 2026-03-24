from pydantic import BaseModel
from typing import List


class PetitionRequest(BaseModel):
    type: str
    tribunal: str
    facts: str
    requests: List[str]


class Precedent(BaseModel):
    title: str
    similarity_score: float
    link: str


class AnalysisResponse(BaseModel):
    status: str
    message: str
    suggested_precedents: List[Precedent]
