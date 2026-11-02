from fastapi import FastAPI, HTTPException
from google.genai import errors
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.gemini import generate_response
import logging

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

@app.post("/api/v1/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        answer = generate_response(request.message)

        return ChatResponse(
            question=request.message,
            answer=answer,
            model="gemini-3.5-flash-lite"
        )

    except errors.APIError as exc:
        if exc.code == 503:
            raise HTTPException(
                status_code=503,
                detail="AI service is temporarily unavailable."
            ) from exc

        raise HTTPException(
            status_code=502,
            detail="AI provider returned an error."
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred."
        ) from exc