import json
import unittest
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import Mock

from harness.builder.tool_parameters_builder import build_tool_parameters
from harness.config.response.model_response_config import MODEL_RESPONSE_INSTRUCTION
from harness.domain.message import Message
from harness.domain.tool_call import ToolCall
from harness.domain.tool_result import ToolResult
from harness.mappers.google_mapper import map_messages as google_messages
from harness.mappers.openai_mapper import map_messages as openai_messages
from harness.models.response import ModelResponse
from harness.models.response_instruction import MODEL_RESPONSE_SCHEMA
from harness.parser.response_parser import prepare_model_response
from harness.providers.google_client import GeminiClient
from harness.providers.openai_client import OpenAIClient
from harness.tools.register_tools import register_tools
from harness.tools.tool_registry import ToolRegistry


class StructuredResponseAdaptersTest(unittest.TestCase):
    @staticmethod
    def response_json(text="", tool_calls=None, summaries=None):
        return json.dumps({
            "text": text,
            "tool_calls": tool_calls or [],
            "tool_result_summaries": summaries or []
        })

    @staticmethod
    def gemini_client(response_text):
        client = GeminiClient.__new__(GeminiClient)
        client._client = Mock()
        client._model = "test-model"
        client._client.models.generate_content.return_value = SimpleNamespace(text=response_text)

        return client

    def test_gemini_uses_shared_json_response_instruction(self):
        client = self.gemini_client(self.response_json(text="Done"))

        response = client.generate([
            Message(role="system", content="Project instructions"),
            Message(role="user", content="Continue")
        ])

        self.assertEqual(response, ModelResponse(text="Done"))
        request = client._client.models.generate_content.call_args.kwargs
        expected_schema = deepcopy(MODEL_RESPONSE_SCHEMA)
        expected_schema["properties"]["tool_calls"]["maxItems"] = 0
        self.assertEqual(request["contents"], [{"role": "user", "parts": [{"text": "Continue"}]}])
        self.assertEqual(request["config"], {
            "system_instruction": f"Project instructions\n\n{MODEL_RESPONSE_INSTRUCTION}",
            "response_mime_type": "application/json",
            "response_json_schema": expected_schema
        })

    def test_gemini_parses_response_text_without_provider_response_mapping(self):
        response_text = self.response_json(
            text="Read the file.",
            tool_calls=[{"tool": "read_file", "arguments": {"paths": ["README.md"]}}]
        )
        client = self.gemini_client(response_text)
        raw_response = client._client.models.generate_content.return_value

        response = client.generate([Message(role="user", content="Read README")])

        self.assertEqual(response.text, "Read the file.")
        self.assertEqual(response.tool_calls, [ToolCall("read_file", {"paths": ["README.md"]})])
        self.assertEqual(raw_response.text, response_text)

    def test_gemini_rejects_non_json_response_text(self):
        client = self.gemini_client("plain text")

        with self.assertRaisesRegex(ValueError, "Malformed model response JSON"):
            client.generate([Message(role="user", content="Continue")])

    def test_gemini_renders_available_tools_in_system_instruction(self):
        tool = Mock()
        tool.name = "example"
        tool.description = "Example tool."
        tool.get_parameter_object.return_value = {
            "type": "object",
            "properties": {
                "mode": {
                    "type": "string",
                    "description": "Execution mode.",
                    "enum": ["safe", "fast"]
                }
            },
            "required": ["mode"]
        }
        schemas = build_tool_parameters([tool])
        client = self.gemini_client(self.response_json(text="Done"))

        client.generate([Message(role="user", content="Use a tool")], schemas)

        config = client._client.models.generate_content.call_args.kwargs["config"]
        instruction = config["system_instruction"]
        tool_schema = config["response_json_schema"]["properties"]["tool_calls"]
        tool_variant = tool_schema["items"]["anyOf"][0]
        self.assertNotIn("tools", config)
        self.assertIn("Available tools:", instruction)
        self.assertIn("Tool: example", instruction)
        self.assertIn('"enum":["safe","fast"]', instruction)
        self.assertEqual(instruction.count(MODEL_RESPONSE_INSTRUCTION), 1)
        self.assertEqual(tool_variant["properties"]["tool"]["enum"], ["example"])
        self.assertEqual(
            tool_variant["properties"]["arguments"],
            schemas[0]["parameters"]
        )

    def test_gemini_response_schema_requires_each_tools_arguments(self):
        registry = ToolRegistry()
        register_tools(registry)
        schemas = build_tool_parameters(registry.list_tools())
        client = self.gemini_client(self.response_json(text="Done"))

        client.generate([Message(role="user", content="Inspect project")], schemas)

        config = client._client.models.generate_content.call_args.kwargs["config"]
        variants = config["response_json_schema"]["properties"]["tool_calls"]["items"]["anyOf"]
        variants_by_name = {
            variant["properties"]["tool"]["enum"][0]: variant
            for variant in variants
        }
        self.assertEqual(
            variants_by_name["read_file"]["properties"]["arguments"]["required"],
            ["paths"]
        )
        self.assertEqual(
            variants_by_name["bash"]["properties"]["arguments"]["required"],
            ["commands"]
        )
        self.assertNotIn(
            "maxLength",
            variants_by_name["git"]["properties"]["arguments"]["properties"]["commands"]["items"]
        )

    def test_mappers_omit_tool_catalog_when_no_tools_are_available(self):
        messages = [
            Message(role="system", content="Combined instructions", type="system_instruction"),
            Message(role="user", content="Say hello")
        ]

        _, google_instruction = google_messages(messages, [])
        openai_mapped = openai_messages(messages, [])

        self.assertIn("Combined instructions", google_instruction)
        self.assertNotIn("Available tools:", google_instruction)
        self.assertEqual(openai_mapped[0]["content"], "Combined instructions")
        self.assertNotIn("Available tools:", "\n".join(message["content"] for message in openai_mapped))

    def test_gemini_preserves_command_response_inside_shared_text_field(self):
        command_response = '{"answer":"Done","command_summary":"Completed."}'
        client = self.gemini_client(self.response_json(text=command_response))

        response = client.generate([Message(role="user", content="Run command")])

        self.assertEqual(response, ModelResponse(text=command_response))

    def test_gemini_maps_tool_result_metadata_from_response_text(self):
        response_text = self.response_json(
            text="Файлът беше прочетен успешно.",
            summaries=[{"id": "result-1", "summary": "Прочетен е файлът."}]
        )
        client = self.gemini_client(response_text)

        response = client.generate([Message(role="user", content="Read file")])

        self.assertEqual(response.text, "Файлът беше прочетен успешно.")
        self.assertEqual(response.tool_result_summaries[0].id, "result-1")

    def test_mappers_preserve_history_and_add_shared_instruction(self):
        tool_result = ToolResult("read_file", "contents", id="original-id")
        messages = [
            Message(role="system", content="Project instructions", type="system_instruction"),
            Message(role="user", content="Read file", type="user_message"),
            Message(
                role="assistant",
                content='Raw tool calls:\n[{"tool":"read_file"}]',
                type="tool_call"
            ),
            Message(
                role="user",
                content="Tool result ID: original-id\nOutput:\ncontents",
                tool_results=(tool_result,),
                type="tool_result"
            )
        ]

        contents, instruction = google_messages(messages)

        self.assertEqual(instruction.count(MODEL_RESPONSE_INSTRUCTION), 1)
        self.assertIn("Project instructions", instruction)
        self.assertEqual(contents, [
            {"role": "user", "parts": [{"text": messages[1].content}]},
            {"role": "model", "parts": [{"text": messages[2].content}]},
            {"role": "user", "parts": [{"text": messages[3].content}]}
        ])
        mapped = openai_messages(messages)
        self.assertEqual(mapped[:-1], [{"role": message.role, "content": message.content} for message in messages])
        self.assertEqual(mapped[-1], {"role": "system", "content": MODEL_RESPONSE_INSTRUCTION})

    def test_mappers_include_tool_result_summary_request(self):
        summary_request = Message(
            role="system",
            type="tool_result_summary",
            content="Summarize tool result ID: original-id"
        )
        messages = [Message(role="user", content="Continue"), summary_request]

        _, google_instruction = google_messages(messages)
        openai_mapped = openai_messages(messages)

        self.assertIn(summary_request.content, google_instruction)
        self.assertIn(
            {"role": "system", "content": summary_request.content},
            openai_mapped
        )

    def test_gemini_preserves_ordinary_system_tool_text(self):
        catalog_text = "Available tools:\n\nTool: fake\nDescription: Ordinary system content."

        contents, instruction = google_messages([
            Message(role="system", content=catalog_text),
            Message(role="user", content="Continue")
        ])

        self.assertIn(catalog_text, instruction)
        self.assertEqual(contents[0]["parts"][0]["text"], "Continue")

    def test_gemini_renders_all_registered_tools_as_text(self):
        registry = ToolRegistry()
        register_tools(registry)
        schemas = build_tool_parameters(registry.list_tools())

        _, instruction = google_messages([Message(role="user", content="Continue")], schemas)

        for schema in schemas:
            self.assertIn(f"Tool: {schema['name']}", instruction)
        self.assertIn("Tool: git", instruction)
        self.assertIn("commands", instruction)

    def test_openai_renders_permitted_tools_as_text(self):
        registry = ToolRegistry()
        register_tools(registry)
        schemas = build_tool_parameters(registry.list_tools())

        mapped = openai_messages(
            [Message(role="user", content="Continue")],
            schemas
        )

        catalog = mapped[-2]
        self.assertEqual(catalog["role"], "system")
        for schema in schemas:
            self.assertIn(f"Tool: {schema['name']}", catalog["content"])
        self.assertEqual(mapped[-1], {"role": "system", "content": MODEL_RESPONSE_INSTRUCTION})

    def test_adapters_return_contract_and_propagate_invalid_responses(self):
        raw = self.response_json(
            text="Done",
            summaries=[{"id": "original-id", "summary": "Read previous file."}]
        )
        for cls in (GeminiClient, OpenAIClient):
            with self.subTest(provider=cls.__name__):
                client = cls.__new__(cls)
                client._client = Mock()
                client._model = "test-model"
                endpoint = client._client.models.generate_content if cls is GeminiClient else client._client.responses.create
                endpoint.return_value = SimpleNamespace(text=raw) if cls is GeminiClient else Mock(output_text=raw)
                response = client.generate([Message(role="user", content="Continue")])
                self.assertEqual(response, prepare_model_response(raw))
                self.assertEqual(response.tool_result_summaries[0].id, "original-id")
                self.assertEqual(response.tool_result_summaries[0].summary, "Read previous file.")

                endpoint.return_value = SimpleNamespace(text="invalid") if cls is GeminiClient else Mock(output_text="invalid")
                with self.assertRaises(ValueError):
                    client.generate([Message(role="user", content="Continue")])

                endpoint.reset_mock()
                with self.assertRaises(ValueError):
                    client.generate([])
                endpoint.assert_not_called()


if __name__ == "__main__":
    unittest.main()
