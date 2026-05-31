from pydantic import BaseModel


class GenerateSentenceRequest(BaseModel):
    user_id: int
    author: str
    defendant: str
    action_type: str
    tribunal: str
    facts_summary: str
    requests: list[str] = []
    precedents: list[dict] = []
    contestacao: str | None = None


class EditSentenceRequest(BaseModel):
    sentence_id: int
    content: str
    change: str
