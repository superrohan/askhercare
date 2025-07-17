
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    personality_mode: Literal["doctor", "bestie", "sister"] = Field(default="doctor")
    category: Optional[str] = Field(default=None)
    conversation_id: Optional[str] = Field(default=None)

class Source(BaseModel):
    content: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ChatResponse(BaseModel):
    message: str
    sources: List[Source] = Field(default_factory=list)
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    personality_mode: str
    timestamp: datetime = Field(default_factory=datetime.now)

class SimplifyRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)

class HealthCategory(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    keywords: List[str] = Field(default_factory=list)