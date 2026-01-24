from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CatalogProductResponse(BaseModel):
    provider: str
    model: Optional[str] = None
    catalog: Dict[str, Any] = Field(default_factory=dict)
    raw_response: str


class NLPSQLRequest(BaseModel):
    question: str = Field(..., min_length=1)
    schema_context: Optional[str] = None
    dialect: str = Field(default="postgresql")


class NLPSQLResponse(BaseModel):
    provider: str
    model: Optional[str] = None
    sql: str
    notes: Optional[str] = None
    raw_response: str


class ExecuteSQLRequest(BaseModel):
    sql: str = Field(..., min_length=1)


class ExecuteSQLResponse(BaseModel):
    sql: str
    row_count: int
    rows: List[Dict[str, Any]]
