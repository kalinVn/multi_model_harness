from typing import Any


class GeminiResponseValidator:
    @staticmethod
    def validate(response: Any, response_text: str, native_function_calls: bool) -> None:
        """Validate that Gemini returned text or native function calls."""

        if response_text.strip() or native_function_calls:
            return

        details = []
        if response.prompt_feedback and response.prompt_feedback.block_reason:
            details.append(f"block_reason={response.prompt_feedback.block_reason}")
        for candidate in response.candidates or []:
            if candidate.finish_reason:
                details.append(f"finish_reason={candidate.finish_reason}")

        suffix = f" ({', '.join(details)})" if details else ""
        raise ValueError(f"Gemini returned no response text{suffix}")
