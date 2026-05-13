from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Petition(Base):
    __tablename__ = "petitions"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=True)
    tribunal = Column(String, nullable=True)
    facts = Column(Text, nullable=True)
    requests = Column(Text, nullable=True)
    precedents = Column(Text, nullable=True)
    petition_path = Column(String, nullable=True)
    user_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )
