from uuid import UUID

from google.genai import errors
from sqlalchemy import select

from app.database.models import Message


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy",
        "application": "Atlumis AI"
    }


def test_chat_endpoint(client, db_session, monkeypatch):
    received_history = []

    def mock_generate_response(history):
        received_history.extend(history)
        return "Merhaba! Sana nasıl yardımcı olabilirim?"

    monkeypatch.setattr(
        "app.main.generate_response",
        mock_generate_response
    )

    response = client.post(
        "/api/v1/chat",
        json={
            "message": "Merhaba!"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == "Merhaba!"
    assert data["answer"] == (
        "Merhaba! Sana nasıl yardımcı olabilirim?"
    )
    assert data["model"] == "gemini-3.5-flash-lite"

    conversation_id = UUID(data["conversation_id"])

    assert received_history == [
        {
            "role": "user",
            "content": "Merhaba!"
        }
    ]

    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.id)
    )

    messages = db_session.scalars(statement).all()

    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[0].content == "Merhaba!"
    assert messages[1].role == "model"
    assert messages[1].content == (
        "Merhaba! Sana nasıl yardımcı olabilirim?"
    )


def test_chat_conversation_continuity(client, db_session, monkeypatch):
    received_histories = []

    def mock_generate_response(history):
        received_histories.append(list(history))

        if len(history) == 1:
            return "Memnun oldum Ahmet!"

        return "Adın Ahmet!"

    monkeypatch.setattr(
        "app.main.generate_response",
        mock_generate_response
    )

    # İlk mesaj
    first_response = client.post(
        "/api/v1/chat",
        json={
            "message": "Benim adım Ahmet."
        }
    )

    assert first_response.status_code == 200

    conversation_id = first_response.json()["conversation_id"]

    # İkinci mesaj: Aynı konuşma kimliği
    second_response = client.post(
        "/api/v1/chat",
        json={
            "message": "Benim adım neydi?",
            "conversation_id": conversation_id
        }
    )

    assert second_response.status_code == 200

    assert second_response.json()["answer"] == "Adın Ahmet!"

    # İlk istekte yalnızca ilk kullanıcı mesajı gönderilmeli
    assert len(received_histories[0]) == 1

    # İkinci istekte önceki mesajlar ve yeni soru bulunmalı
    assert received_histories[1] == [
        {
            "role": "user",
            "content": "Benim adım Ahmet."
        },
        {
            "role": "model",
            "content": "Memnun oldum Ahmet!"
        },
        {
            "role": "user",
            "content": "Benim adım neydi?"
        }
    ]

    # Veritabanında toplam dört mesaj bulunmalı
    statement = (
        select(Message)
        .where(
            Message.conversation_id == conversation_id
        )
        .order_by(Message.id)
    )

    messages = db_session.scalars(statement).all()

    assert len(messages) == 4


def test_chat_rejects_empty_message(client):
    response = client.post(
        "/api/v1/chat",
        json={
            "message": ""
        }
    )

    assert response.status_code == 422


def test_chat_rejects_message_over_max_length(client):
    response = client.post(
        "/api/v1/chat",
        json={
            "message": "A" * 4001
        }
    )

    assert response.status_code == 422


def test_chat_handles_unexpected_gemini_error(client, db_session, monkeypatch):

    def mock_generate_response(history):
        raise RuntimeError("Simulated Gemini failure")

    monkeypatch.setattr(
        "app.main.generate_response",
        mock_generate_response
    )

    response = client.post(
        "/api/v1/chat",
        json={
            "message": "Merhaba!"
        }
    )

    assert response.status_code == 500

    assert response.json() == {
        "detail": "An unexpected error occurred."
    }

    # Gemini başarısız olduğunda mesaj kaydedilmemeli.
    messages = db_session.scalars(
        select(Message)
    ).all()

    assert len(messages) == 0


def test_chat_handles_gemini_503_error(client, monkeypatch):

    def mock_generate_response(history):
        raise errors.APIError(
            503,
            {"message": "Service unavailable"}
        )

    monkeypatch.setattr(
        "app.main.generate_response",
        mock_generate_response
    )

    response = client.post(
        "/api/v1/chat",
        json={"message": "Merhaba!"}
    )

    assert response.status_code == 503

    assert response.json() == {
        "detail": "AI service is temporarily unavailable."
    }


def test_chat_handles_gemini_429_error(client, monkeypatch):

    def mock_generate_response(history):
        raise errors.APIError(
            429,
            {"message": "Rate limit exceeded"}
        )

    monkeypatch.setattr(
        "app.main.generate_response",
        mock_generate_response
    )

    response = client.post(
        "/api/v1/chat",
        json={"message": "Merhaba!"}
    )

    assert response.status_code == 429

    assert response.json() == {
        "detail": "AI service rate limit exceeded."
    }
