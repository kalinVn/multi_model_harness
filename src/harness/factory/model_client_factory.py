import os

from harness.models.model_client import ModelClient
from harness.factory.schema_builder_factory import SchemaBuilderFactory
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
        return GeminiClient(
            schema_builder=SchemaBuilderFactory.create(provider),
        )

    if provider == "openai":
        return OpenAIClient()

    if provider == "groq":
        return GroqClient(
            schema_builder=SchemaBuilderFactory.create(provider),
        )

    raise ValueError(f"Unsupported MODEL_PROVIDER: {provider}")
