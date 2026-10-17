import os

import httpx
from google import genai
from google.genai import types
from google.genai.errors import ClientError, ServerError

from harness.domain.message import Message
from harness.models.errors import (
    ModelConnectionError,
    ModelRateLimitError,
)
from harness.models.response import ModelResponse
from harness.parser.response_parser import (
    parse_model_response,
)
from harness.mappers.google_mapper import (
    map_messages,
)


class GeminiClient:
    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("Missing GEMINI_API_KEY")

        timeout_seconds = int(os.getenv("GEMINI_TIMEOUT_SECONDS", "30"))

        self._client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=timeout_seconds * 1000,
                retry_options=types.HttpRetryOptions(
                    attempts=4,
                    initial_delay=1.0,
                    max_delay=8.0,
                    exp_base=2.0,
                    jitter=1.0,
                    http_status_codes=[500, 502, 503, 504],
                ),
            ),
        )

        self._model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    def generate(
        self,
        messages: list[Message],
    ) -> ModelResponse:
        contents, system_instruction = map_messages(messages)

        if not contents:
            raise ValueError("Cannot generate response with empty conversation.")

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
        )

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=contents,
                config=config,
            )
        except ClientError as error:
            if error.code == 404:
                raise ModelConnectionError(
                    f"Gemini model '{self._model}' was not found or does not support "
                    "generateContent. Check GEMINI_MODEL in .env against the models "
                    "available to your API key, then restart the harness."
                ) from error
            if error.code != 429:
                raise

            raise ModelRateLimitError(
                "Gemini request quota exceeded. "
                "Wait for the cooldown shown by Gemini, then retry, "
                "or increase the API project's quota/billing."
            ) from error
        except ServerError as error:
            raise ModelConnectionError(
                "Gemini is temporarily unavailable or experiencing high demand. "
                "Please try again later."
            ) from error
        except httpx.HTTPError as error:
            raise ModelConnectionError(
                "Gemini could not be reached. "
                "Check the internet connection and try again."
            ) from error

        response_text = response.text or ""

        if not response_text.strip():
            details = []
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                details.append(f"block_reason={response.prompt_feedback.block_reason}")
            for candidate in response.candidates or []:
                if candidate.finish_reason:
                    details.append(f"finish_reason={candidate.finish_reason}")
            suffix = f" ({', '.join(details)})" if details else ""
            raise ValueError(f"Gemini returned no response text{suffix}")

        try:
            return parse_model_response(response_text)
        except ValueError as error:
            raise ValueError(f"Gemini returned an invalid model response: {error}") from error
