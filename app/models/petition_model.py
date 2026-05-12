from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Petition(Base):
    __tablename__ = "petitions"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    tribunal = Column(String)
    facts = Column(String)
    requests = Column(String)
    file_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="petitions")
