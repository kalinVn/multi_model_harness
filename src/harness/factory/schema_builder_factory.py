from harness.builder.gemini_schema_builder import GeminiSchemaBuilder
from harness.builder.groq_schema_builder import GroqSchemaBuilder


class SchemaBuilderFactory:
    """Select a provider-specific tool schema builder."""

    @staticmethod
    def create(provider: str) -> GroqSchemaBuilder | GeminiSchemaBuilder:
        normalized_provider = provider.strip().lower()

        if normalized_provider == "groq":
            return GroqSchemaBuilder()
        if normalized_provider in {"google", "gemini"}:
            return GeminiSchemaBuilder()

        raise ValueError(f"Unsupported schema provider: {provider}")
