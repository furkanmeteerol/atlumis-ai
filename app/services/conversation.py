from typing import TypedDict
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Conversation, Message as MessageModel


class MessageData(TypedDict):
    role: str
    content: str


def get_history(
    db: Session,
    conversation_id: UUID
) -> list[MessageData]:

    statement = (
        select(MessageModel)
        .where(MessageModel.conversation_id == conversation_id)
        .order_by(MessageModel.id)
    )

    messages = db.scalars(statement).all()

    return [
        {
            "role": message.role,
            "content": message.content
        }
        for message in messages
    ]


def save_turn(
    db: Session,
    conversation_id: UUID,
    question: str,
    answer: str
) -> None:

    try:
        conversation = db.get(Conversation, conversation_id)

        if conversation is None:
            conversation = Conversation(id=conversation_id)
            db.add(conversation)

        user_message = MessageModel(
            conversation_id=conversation_id,
            role="user",
            content=question
        )

        model_message = MessageModel(
            conversation_id=conversation_id,
            role="model",
            content=answer
        )

        db.add_all([user_message, model_message])
        db.commit()

    except Exception:
        db.rollback()
        raise