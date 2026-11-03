from typing import NoReturn

import httpx
from google.genai.errors import ClientError, ServerError

from harness.models.errors import ModelConnectionError, ModelRateLimitError


class GeminiErrorValidator:
    @staticmethod
    def validate(error: Exception, model: str) -> NoReturn:
        """Classify a Gemini SDK error and raise the appropriate exception."""

        if isinstance(error, ClientError):
            if error.code == 404:
                raise ModelConnectionError(
                    f"Gemini model '{model}' was not found or does not support "
                    "generateContent. Check GEMINI_MODEL in .env against the models "
                    "available to your API key, then restart the harness."
                ) from error
            if error.code != 429:
                raise error

            raise ModelRateLimitError(
                "Gemini request quota exceeded. "
                "Wait for the cooldown shown by Gemini, then retry, "
                "or increase the API project's quota/billing."
            ) from error

        if isinstance(error, ServerError):
            raise ModelConnectionError(
                "Gemini is temporarily unavailable or experiencing high demand. "
                "Please try again later."
            ) from error

        if isinstance(error, httpx.HTTPError):
            raise ModelConnectionError(
                "Gemini could not be reached. "
                "Check the internet connection and try again."
            ) from error

        raise error
