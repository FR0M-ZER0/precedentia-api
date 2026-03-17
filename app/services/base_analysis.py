from abc import ABC, abstractmethod
from app.schemas.petition_schema import PetitionRequest

class BaseAnalysisService(ABC):
    @abstractmethod
    async def process_petition(self, data: PetitionRequest):
        pass