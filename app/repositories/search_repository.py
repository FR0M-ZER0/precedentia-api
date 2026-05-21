import json

from sqlalchemy.orm import Session

from app.models.search_model import Search


class SearchRecord:
    def __init__(
        self,
        user_id: int,
        precedents: list[str],
        petition_path: str | None = None,
    ):
        self.user_id = user_id
        self.petition_path = petition_path
        self.precedents = precedents
        self.type: str | None = None
        self.tribunal: str | None = None
        self.facts: str | None = None
        self.requests: str | None = None


class SearchRepository:
    def save(self, record: SearchRecord, db: Session) -> Search:
        db_search = Search(
            user_id=record.user_id,
            petition_path=record.petition_path,
            precedents=json.dumps(record.precedents),
            type=record.type,
            tribunal=record.tribunal,
            facts=record.facts,
            requests=record.requests,
        )
        db.add(db_search)
        db.commit()
        db.refresh(db_search)
        return db_search


search_repository = SearchRepository()
