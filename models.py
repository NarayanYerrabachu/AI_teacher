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


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    use_rag: bool = True


class ChatResponse(BaseModel):
    response: str
    session_id: str
    sources: Optional[List[dict]] = None

