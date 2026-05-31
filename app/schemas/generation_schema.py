from pydantic import BaseModel, ConfigDict


class PrecedentInput(BaseModel):
    name: str
    question: str
    description: str


class PetitionGenerationBase(BaseModel):
    author_description: str
    defendant_description: str
    action_type: str
    tribunal: str
    facts_summary: str
    requests: str
    value_of_cause: str
    urgent_relief: bool
    free_justice: bool
    precedents: list[PrecedentInput]


class PetitionEditRequest(BaseModel):
    id: int
    change: str
    content: str


class PetitionResponse(BaseModel):
    id: int
    content: str
    user_id: int

    model_config = ConfigDict(from_attributes=True)
