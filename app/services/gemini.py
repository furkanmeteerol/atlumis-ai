
import logging
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.services.conversation import MessageData

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not configured.")

client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(
        timeout=30000,
        retry_options=types.HttpRetryOptions(
            attempts=3,
            initial_delay=1.0,
            max_delay=4.0,
            exp_base=2.0,
            http_status_codes=[408, 429, 500, 502, 503, 504]
        )
    )
)

MODEL_NAME = "gemini-3.5-flash-lite"

logger = logging.getLogger(__name__)


def generate_response(history: list[MessageData]) -> str:
    logger.info("Gemini request started")

    contents = [
        types.Content(
            role=message["role"],
            parts=[
                types.Part.from_text(text=message["content"])
            ]
        )
        for message in history
    ]

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents
        )

        answer = response.text or ""

        logger.info("Gemini response received successfully")

        return answer

    except Exception:
        logger.exception("Gemini request failed")
        raise
