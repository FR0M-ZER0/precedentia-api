from pydantic import BaseModel


class GenerateSentenceRequest(BaseModel):
    author: str
    defendant: str
    action_type: str
    tribunal: str
    facts_summary: str
    requests: list[str] = []
    precedents: list[dict] = []
    contestacao: str | None = None


class EditSentenceRequest(BaseModel):
    content: str
    change: str
