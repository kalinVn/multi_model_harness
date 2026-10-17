import os

from harness.models.model_client import ModelClient
from harness.providers.google_client import (
    GeminiClient,
)
from harness.providers.openai_client import (
    OpenAIClient,
)

from harness.providers.groq_client import (
    GroqClient,
)


def create_model_client() -> ModelClient:
    provider = os.getenv("MODEL_PROVIDER", "google").lower()

    if provider in {"google", "gemini"}:
        return GeminiClient()

    if provider == "openai":
        return OpenAIClient()

    if provider == "groq":
        return GroqClient()

    raise ValueError(f"Unsupported MODEL_PROVIDER: {provider}")
