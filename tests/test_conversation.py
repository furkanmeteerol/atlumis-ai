from uuid import uuid4

from sqlalchemy import select

from app.database.models import Conversation, Message
from app.services.conversation import save_turn, get_history


def test_save_turn(db_session):
    conversation_id = uuid4()

    save_turn(
        db=db_session,
        conversation_id=conversation_id,
        question="Benim adım Ahmet.",
        answer="Memnun oldum Ahmet!"
    )

    conversation = db_session.get(Conversation, conversation_id)

    assert conversation is not None

    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.id)
    )

    messages = db_session.scalars(statement).all()

    assert len(messages) == 2

    assert messages[0].role == "user"
    assert messages[0].content == "Benim adım Ahmet."

    assert messages[1].role == "model"
    assert messages[1].content == "Memnun oldum Ahmet!"


def test_get_history(db_session):
    conversation_id = uuid4()

    save_turn(
        db=db_session,
        conversation_id=conversation_id,
        question="Benim adım Ahmet.",
        answer="Memnun oldum Ahmet!"
    )

    history = get_history(
        db=db_session,
        conversation_id=conversation_id
    )

    assert len(history) == 2

    assert history[0] == {
        "role": "user",
        "content": "Benim adım Ahmet."
    }

    assert history[1] == {
        "role": "model",
        "content": "Memnun oldum Ahmet!"
    }


def test_get_history_returns_empty_list(db_session):
    conversation_id = uuid4()

    history = get_history(
        db=db_session,
        conversation_id=conversation_id
    )

    assert history == []