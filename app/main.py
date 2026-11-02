from fastapi import FastAPI

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