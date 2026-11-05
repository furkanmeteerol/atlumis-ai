import logging
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, UploadFile, File
from google.genai import errors
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.gemini import generate_response, MODEL_NAME
from app.services.conversation import get_history, save_turn
from app.schemas.document import DocumentResponse
from app.services.document import (
    create_document,
    DocumentValidationError
)
from app.storage.local import LocalStorage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="Atlumis AI",
    description="Enterprise AI Assistant Platform",
    version="0.1.0"
)

@app.get("/")
def root():
    return {
        "message": "Welcome to Atlumis AI!",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "Atlumis AI"
    }


storage = LocalStorage()

@app.post(
    "/api/v1/documents/upload",
    response_model=DocumentResponse
)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    filename = file.filename or ""

    try:
        content = await file.read(10 * 1024 * 1024 + 1)

        document = create_document(
            db=db,
            storage=storage,
            filename=filename,
            content_type=file.content_type,
            content=content
        )

        return document

    except DocumentValidationError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc

    except Exception as exc:
        logging.exception("Document upload failed")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred."
        ) from exc

    finally:
        await file.close()


@app.post("/api/v1/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    conversation_id = request.conversation_id or uuid4()

    try:
        history = get_history(db, conversation_id)

        history_with_new_message = history + [
            {
                "role": "user",
                "content": request.message
            }
        ]

        answer = generate_response(history_with_new_message)

        save_turn(
            db=db,
            conversation_id=conversation_id,
            question=request.message,
            answer=answer
        )

        return ChatResponse(
            conversation_id=conversation_id,
            question=request.message,
            answer=answer,
            model=MODEL_NAME
        )

    except errors.APIError as exc:
        if exc.code == 503:
            raise HTTPException(
                status_code=503,
                detail="AI service is temporarily unavailable."
            ) from exc

        if exc.code == 429:
            raise HTTPException(
                status_code=429,
                detail="AI service rate limit exceeded."
            ) from exc

        raise HTTPException(
            status_code=502,
            detail="AI provider returned an error."
        ) from exc

    except Exception as exc:
        logging.exception("Chat endpoint failed")

        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred."
        ) from exc
