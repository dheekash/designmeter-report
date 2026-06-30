"""SQLAlchemy ORM models for Interview Helper."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Integer, String, Text, create_engine, Index
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class QuestionRecord(Base):
    """One question + answer pair stored from the interview session."""

    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False, default="General")
    answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    provider: Mapped[str] = mapped_column(String(32), default="openai")
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    tags: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)  # comma-separated
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_questions_category", "category"),
        Index("ix_questions_favorite", "is_favorite"),
        Index("ix_questions_created", "created_at"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "question": self.question,
            "category": self.category,
            "answer": self.answer,
            "provider": self.provider,
            "is_favorite": self.is_favorite,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
