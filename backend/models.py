# Pydantic models
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from .config import Config

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
    image_data: Optional[str] = None  # Base64 encoded image
    extracted_text: Optional[str] = None  # OCR extracted text from image


class ChatResponse(BaseModel):
    response: str
    session_id: str
    sources: Optional[List[dict]] = None
    explanation_animation: Optional[dict] = None  # Animation steps data
    explanation_audio: Optional[str] = None  # Base64 encoded audio
    explanation_duration: Optional[float] = None  # Duration in seconds


class StudioGenerateRequest(BaseModel):
    session_id: str
    content_type: str  # "summary", "quiz", "flashcards", "report"


class StudioGenerateResponse(BaseModel):
    success: bool
    data: dict
    message: Optional[str] = None


class ExplanationGenerateRequest(BaseModel):
    message: str  # User's question
    answer: str  # Assistant's answer


class ExplanationGenerateResponse(BaseModel):
    success: bool
    animation: Optional[dict] = None  # Animation steps data
    audio: Optional[str] = None  # Base64 encoded audio
    duration: Optional[float] = None  # Duration in seconds
    message: Optional[str] = None

