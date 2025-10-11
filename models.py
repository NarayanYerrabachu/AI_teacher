# Pydantic models
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from config import Config

class WebPageRequest(BaseModel):
    urls: List[HttpUrl]


class QueryRequest(BaseModel):
    query: str
    k: Optional[int] = Config.DEFAULT_SEARCH_K


class QueryResponse(BaseModel):
    query: str
    results: List[dict]
    total_results: int


class StatusResponse(BaseModel):
    status: str
    message: str
    details: Optional[dict] = None

