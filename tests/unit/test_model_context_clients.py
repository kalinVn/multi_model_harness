import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from harness.config.model_context_config import OPENAI_MODEL_CONTEXT_LIMITS
from harness.domain.context import ModelContextLimits
from harness.domain.message import Message
from harness.mappers.google_mapper import map_messages as google_messages
from harness.mappers.openai_mapper import map_messages as openai_messages
from harness.providers.google_client import GeminiClient, _build_response_schema
from harness.providers.openai_client import OpenAIClient


class ModelContextClientsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.messages = [
            Message(role="system", content="Project instructions"),
            Message(role="user", content="Continue")
        ]
        self.tools = [{
            "name": "read_file",
            "description": "Reads files.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }]

    def test_openai_counts_the_same_prepared_input_used_for_generation(self):
        client = OpenAIClient.__new__(OpenAIClient)
        client._client = Mock()
        client._model = "test-model"
        client._client.responses.input_tokens.count.return_value = SimpleNamespace(input_tokens=123)

        count = client.count_tokens(self.messages, self.tools)

        self.assertEqual(count, 123)
        client._client.responses.input_tokens.count.assert_called_once_with(
            model="test-model",
            input=openai_messages(self.messages, self.tools)
        )

    def test_openai_uses_defaults_and_per_field_environment_overrides(self):
        client = OpenAIClient.__new__(OpenAIClient)
        client._model = "gpt-5.5"
        default_context_window, default_reserved_output = OPENAI_MODEL_CONTEXT_LIMITS[client._model]

        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(
                client.get_context_limits(),
                ModelContextLimits(client._model, default_context_window, default_reserved_output)
            )

        with patch.dict(
            os.environ,
            {
                "OPENAI_CONTEXT_WINDOW": "2000",
                "OPENAI_RESERVED_OUTPUT_TOKENS": "300"
            },
            clear=True
        ):
            self.assertEqual(
                client.get_context_limits(),
                ModelContextLimits(client._model, 2_000, 300)
            )

        with patch.dict(os.environ, {"OPENAI_CONTEXT_WINDOW": "2000"}, clear=True):
            self.assertEqual(
                client.get_context_limits(),
                ModelContextLimits(client._model, 2_000, default_reserved_output)
            )

    def test_openai_unknown_model_requires_both_explicit_limits(self):
        client = OpenAIClient.__new__(OpenAIClient)
        client._model = "unknown-model"

        environments = [
            {},
            {"OPENAI_CONTEXT_WINDOW": "2000"},
            {"OPENAI_RESERVED_OUTPUT_TOKENS": "300"}
        ]
        for environment in environments:
            with self.subTest(environment=environment), patch.dict(os.environ, environment, clear=True):
                with self.assertRaisesRegex(ValueError, "Set OPENAI_CONTEXT_WINDOW"):
                    client.get_context_limits()

    def test_gemini_counts_contents_and_serialized_hidden_context_without_config(self):
        client = GeminiClient.__new__(GeminiClient)
        client._client = Mock()
        client._model = "test-model"
        client._client.models.count_tokens.return_value = SimpleNamespace(total_tokens=321)

        count = client.count_tokens(self.messages, self.tools)

        contents, system_instruction = google_messages(self.messages, self.tools)
        request = client._client.models.count_tokens.call_args.kwargs
        hidden_context = request["contents"][0]["parts"][0]["text"]
        self.assertEqual(count, 321)
        self.assertEqual(request["model"], "test-model")
        self.assertEqual(request["contents"][1:], contents)
        self.assertIn(system_instruction, hidden_context)
        self.assertIn(
            json.dumps(_build_response_schema(self.tools), ensure_ascii=False, separators=(",", ":")),
            hidden_context
        )
        self.assertNotIn("config", request)

    def test_gemini_reads_separate_input_and_output_limits(self):
        client = GeminiClient.__new__(GeminiClient)
        client._client = Mock()
        client._model = "test-model"
        client._client.models.get.return_value = SimpleNamespace(
            input_token_limit=1_000,
            output_token_limit=200
        )

        limits = client.get_context_limits()

        self.assertEqual(
            limits,
            ModelContextLimits(
                model="test-model",
                context_window=1_000,
                reserved_output_tokens=200,
                input_token_limit=1_000
            )
        )
        client._client.models.get.assert_called_once_with(model="test-model")


if __name__ == "__main__":
    unittest.main()
