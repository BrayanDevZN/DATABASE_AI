from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Literal, List
from datetime import datetime


class CreateConversation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    conversation_id: int = Field(gt=0)
    role: Literal["user", "assistant"]
    content: str

    @field_validator("content")
    def validate_content(cls, v: str):
        if not v.strip():
            raise ValueError("content cannot be empty")
        return v


class WithToken(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str


class GetConversation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str
    conversation_id: int = Field(gt=0)


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    conversation_id: int
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime


class ListMessages(BaseModel):
    messages: List[MessageResponse]


class ConversationSummary(BaseModel):
    conversation_id: int
    created_at: datetime
    updated_at: datetime
    total_messages: int


class ListConversations(BaseModel):
    conversations: List[ConversationSummary]
    
class CreateConversationWithToken(CreateConversation):
    token: str