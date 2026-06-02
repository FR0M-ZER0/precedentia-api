from sqlalchemy import JSON, Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Search(Base):
    __tablename__ = "search"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=True)
    tribunal = Column(String, nullable=True)
    facts = Column(Text, nullable=True)
    requests = Column(Text, nullable=True)
    precedents = Column(JSON, nullable=True)
    petition_path = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )
    owner = relationship("User", back_populates="searches")
