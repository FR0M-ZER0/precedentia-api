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
        page_size: int = 10,
    ):
        pass

    async def stream_petition(self, data, **kwargs):
        result = await self.process_petition(data, **kwargs)
        for idx, precedent in enumerate(result.get("results", [])):
            yield "precedent", {"index": idx, **precedent}
        yield "done", {"total_found": result.get("total_found", 0)}
