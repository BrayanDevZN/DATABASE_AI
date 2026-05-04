from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, field_validator


class CreateConversation(BaseModel):
    user_id: int = Field(gt=0)
    conversation_id: int = Field(gt=0)
    role: Literal["user", "assistant"]
    content: str

    @field_validator("content")
    def valid_content(cls, v: str):
        if not v.strip():
            raise ValueError("content cannot be empty")
        return v


class ConversationResponse(BaseModel):
    id: int
    user_id: int
    conversation_id: int
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime


class ConversationSummary(BaseModel):
    conversation_id: int
    created_at: datetime
    updated_at: datetime
    total_messages: int