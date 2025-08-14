from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class DocumentMetadata(BaseModel):
    filename: str
    file_type: str
    upload_date: datetime
    chunk_count: int
    file_size: int


class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the message sender (user or assistant)")
    content: str = Field(..., description="Content of the message")
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    message: str = Field(..., description="User's chat message")
    conversation_history: Optional[List[ChatMessage]] = []
    stream: bool = Field(default=True, description="Whether to stream the response")


class ChatResponse(BaseModel):
    response: str = Field(..., description="AI response")
    sources: Optional[List[str]] = Field(default=[], description="Source documents used")
    conversation_id: Optional[str] = None


class IngestRequest(BaseModel):
    text_content: Optional[str] = None
    filename: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}


class IngestResponse(BaseModel):
    success: bool
    message: str
    document_id: Optional[str] = None
    chunks_created: int = 0


class RetrievalResult(BaseModel):
    content: str
    metadata: Dict[str, Any]
    score: float


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None 