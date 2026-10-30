from typing import Any

from harness.converter.gemini_tool_converter import GeminiToolConverter
from harness.converter.openai_tool_converter import OpenAIToolConverter
from harness.models.tool_definition import ToolDefinition


class ToolConverterFacade:
    """Select the tool converter for a model provider."""

    def __init__(self) -> None:
        self._converters = {
            "gemini": GeminiToolConverter(),
            "openai": OpenAIToolConverter(),
        }

    def convert_tools(
        self,
        provider: str,
        tools: list[ToolDefinition],
    ) -> Any:
        converter = self._converters.get(provider)
        if converter is None:
            raise ValueError(f"Unsupported tool converter provider: {provider}")

        return converter.convert_tools(tools)
