from pydantic import BaseModel
from typing import List

class Requirement(BaseModel):
    id: str 
    name: str
    description:str

class TestCase(BaseModel):
    id:str
    summary:str


class TraceabilityRequest(BaseModel):
    requirements: List[Requirement]
    test_cases: List[TestCase]



