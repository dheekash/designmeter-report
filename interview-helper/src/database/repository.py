"""Database access layer — all CRUD operations."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import List, Optional

from sqlalchemy import create_engine, or_, desc
from sqlalchemy.orm import Session, sessionmaker

from .models import Base, QuestionRecord
from ..utils.logger import get_logger

log = get_logger("database")


class Repository:
    def __init__(self, db_path: Path):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        engine = create_engine(f"sqlite:///{db_path}", echo=False)
        Base.metadata.create_all(engine)
        self._Session = sessionmaker(bind=engine)
        self._session_id = str(uuid.uuid4())
        log.info("Database ready at %s (session=%s)", db_path, self._session_id)

    @property
    def session_id(self) -> str:
        return self._session_id

    # ---------- write --------------------------------------------------

    def save(self, question: str, category: str, answer: str, provider: str, tags: str = "") -> QuestionRecord:
        with self._Session() as s:
            rec = QuestionRecord(
                session_id=self._session_id,
                question=question,
                category=category,
                answer=answer,
                provider=provider,
                tags=tags,
            )
            s.add(rec)
            s.commit()
            s.refresh(rec)
            log.debug("Saved Q#%d [%s]", rec.id, category)
            return rec

    def toggle_favorite(self, record_id: int) -> bool:
        with self._Session() as s:
            rec = s.get(QuestionRecord, record_id)
            if rec:
                rec.is_favorite = not rec.is_favorite
                s.commit()
                return rec.is_favorite
            return False

    def delete(self, record_id: int) -> bool:
        with self._Session() as s:
            rec = s.get(QuestionRecord, record_id)
            if rec:
                s.delete(rec)
                s.commit()
                return True
            return False

    # ---------- read ---------------------------------------------------

    def search(
        self,
        query: str = "",
        category: Optional[str] = None,
        favorites_only: bool = False,
        limit: int = 200,
    ) -> List[dict]:
        with self._Session() as s:
            q = s.query(QuestionRecord)
            if query:
                like = f"%{query}%"
                q = q.filter(or_(QuestionRecord.question.ilike(like), QuestionRecord.answer.ilike(like)))
            if category:
                q = q.filter(QuestionRecord.category == category)
            if favorites_only:
                q = q.filter(QuestionRecord.is_favorite == True)
            records = q.order_by(desc(QuestionRecord.created_at)).limit(limit).all()
            return [r.to_dict() for r in records]

    def recent(self, n: int = 50) -> List[dict]:
        return self.search(limit=n)

    def all_categories(self) -> List[str]:
        with self._Session() as s:
            rows = s.query(QuestionRecord.category).distinct().all()
            return sorted({r[0] for r in rows})

    def get(self, record_id: int) -> Optional[dict]:
        with self._Session() as s:
            rec = s.get(QuestionRecord, record_id)
            return rec.to_dict() if rec else None
