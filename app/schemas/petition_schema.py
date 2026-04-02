from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Literal

TRIBUNAIS_VALIDOS = Literal[
    "STF",
    "STJ",
    "TST",
    "TSE",
    "STM",
    "TNU",
    "TRF1",
    "TRF2",
    "TRF3",
    "TRF4",
    "TRF5",
    "TRF6",
    "TJAC",
    "TJAL",
    "TJAP",
    "TJAM",
    "TJBA",
    "TJCE",
    "TJDF",
    "TJES",
    "TJGO",
    "TJMA",
    "TJMT",
    "TJMS",
    "TJMG",
    "TJPA",
    "TJPB",
    "TJPR",
    "TJPE",
    "TJPI",
    "TJRJ",
    "TJRN",
    "TJRS",
    "TJRO",
    "TJRR",
    "TJSC",
    "TJSP",
    "TJSE",
    "TJTO",
    "TRT1",
    "TRT2",
    "TRT3",
    "TRT4",
    "TRT5",
    "TRT6",
    "TRT7",
    "TRT8",
    "TRT9",
    "TRT10",
    "TRT11",
    "TRT12",
    "TRT13",
    "TRT14",
    "TRT15",
    "TRT16",
    "TRT17",
    "TRT18",
    "TRT19",
    "TRT20",
    "TRT21",
    "TRT22",
    "TRT23",
    "TRT24",
    "TREs",
    "TJMs",
]


class PetitionRequest(BaseModel):
    type: str = Field(..., example="Ação de Alimentos")
    facts: str = Field(..., example="Resumo dos fatos da petição...")
    text: str = Field(..., example="Conteúdo extraído do PDF...")
    requests: List[str] = Field(..., json_schema_extra={"example": ["danos morais"]})


class Precedent(BaseModel):
    name: str
    tribunal: str
    last_update: datetime
    situation: str
    url: str
    description: str
    score: float


class PaginatedPrecedentsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    precedents: List[Precedent]
