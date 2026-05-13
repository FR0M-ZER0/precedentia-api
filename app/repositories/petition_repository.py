# This module uses a local JSON file as storage while the database is not ready.
# When the database is functional, replace LocalPetitionRepository with
# DBPetitionRepository (see bottom of file) — the interface is identical.

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ── Data class ───────────────────────────────────────────────────────────────

class PetitionRecord:
    """Plain data container — maps 1:1 to the petitions table columns."""

    def __init__(
        self,
        user_id: int,
        petition_path: str,
        precedents: list[str],
    ):
        self.user_id = user_id
        self.petition_path = petition_path
        self.precedents = precedents  # e.g. ["precedent:123", "precedent:456"]
        # Fields filled by other means — kept as None until then
        self.type: Optional[str] = None
        self.tribunal: Optional[str] = None
        self.facts: Optional[str] = None
        self.requests: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "petition_path": self.petition_path,
            "precedents": json.dumps(self.precedents),
            "type": self.type,
            "tribunal": self.tribunal,
            "facts": self.facts,
            "requests": self.requests,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }


# ── Local (JSON file) implementation ─────────────────────────────────────────

_LOCAL_STORAGE_PATH = Path(__file__).resolve().parent.parent.parent / "petitions" / "_records.json"


class LocalPetitionRepository:
    """
    Persists records to a JSON file inside the petitions/ folder.
    No external dependencies — works before the database is ready.
    """

    def save(self, record: PetitionRecord) -> dict:
        # Load existing records (or start fresh)
        records: list[dict] = []
        if _LOCAL_STORAGE_PATH.exists():
            with open(_LOCAL_STORAGE_PATH, "r", encoding="utf-8") as f:
                try:
                    records = json.load(f)
                except json.JSONDecodeError:
                    records = []

        entry = record.to_dict()
        entry["id"] = len(records) + 1  # simple auto-increment placeholder
        records.append(entry)

        with open(_LOCAL_STORAGE_PATH, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

        return entry


# ── Active repository ─────────────────────────────────────────────────────────

# SWAP: when the DB is ready, replace the line below with:
#   petition_repository = DBPetitionRepository()
petition_repository = LocalPetitionRepository()


# ── DB implementation (ready to use when database is functional) ──────────────

# from sqlalchemy.orm import Session
# from app.models.petition_model import Petition
# import json
# import os
#
# class DBPetitionRepository:
#     """
#     Persists records to the database via SQLAlchemy.
#     Interface is identical to LocalPetitionRepository.
#     """
#
#     def save(self, record: PetitionRecord, db: Session) -> Petition:
#         db_petition = Petition(
#             user_id=record.user_id,
#             petition_path=record.petition_path,
#             precedents=json.dumps(record.precedents),
#             type=record.type,
#             tribunal=record.tribunal,
#             facts=record.facts,
#             requests=record.requests,
#         )
#         db.add(db_petition)
#         db.commit()
#         db.refresh(db_petition)
#         return db_petition
