from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=4000,
        description="User message sent to the AI assistant"
    )

    conversation_id: UUID | None = Field(
        default=None,
        description="ID of an existing conversation"
    )


class ChatResponse(BaseModel):
    conversation_id: UUID
    question: str
    answer: str
    model: str
