from sqlalchemy.orm import Session
from app.models.sentence_model import Sentence
from datetime import datetime


class SentenceRepository:
    def save(self, content: str, user_id: int, db: Session) -> Sentence:
        record = Sentence(content=content, user_id=user_id)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def get_by_id(self, sentence_id: int, db: Session) -> Sentence | None:
        return db.query(Sentence).filter(Sentence.id == sentence_id).first()

    def update_content(self, sentence: Sentence, content: str, db: Session) -> Sentence:
        sentence.content = content
        sentence.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(sentence)
        return sentence

    def update_content_by_id(
        self, sentence_id: int, content: str, db: Session
    ) -> Sentence:
        sentence = db.query(Sentence).filter(Sentence.id == sentence_id).first()
        if not sentence:
            raise ValueError(f"Sentença {sentence_id} não encontrada.")
        sentence.content = content
        sentence.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(sentence)
        return sentence


sentence_repository = SentenceRepository()
