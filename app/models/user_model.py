from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )
    two_factor_code = Column(String, nullable=True)
    two_factor_expires = Column(DateTime, nullable=True)

    searches = relationship(
        "Search", back_populates="owner", cascade="all, delete-orphan"
    )
    # petitions = relationship(
    #     "Petition", back_populates="user", cascade="all, delete-orphan"
    # )
