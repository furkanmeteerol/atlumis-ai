from fastapi import FastAPI
from app.schemas.chat import ChatRequest
from app.services.gemini import generate_response

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

@app.post("/api/v1/chat")
def chat(request: ChatRequest):
    answer = generate_response(request.message)

    return {
        "question": request.message,
        "answer": answer,
        "model": "gemini-3.5-flash-lite"
    }