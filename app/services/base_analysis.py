from abc import ABC, abstractmethod
from typing import Optional
from app.schemas.petition_schema import PetitionRequest


class BaseAnalysisService(ABC):
    @abstractmethod
    async def process_petition(
        self, 
        data: PetitionRequest,
        name_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        sort_by_score: bool = True,
        page: int = 1,
        page_size: int = 10
    ):
        pass
