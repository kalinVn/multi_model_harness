import json
import unittest
from unittest.mock import Mock

from google.genai import types

from harness.builder.tools_schema_builder import build_tools_schema
from harness.domain.message import Message
from harness.domain.tool_call import ToolCall
from harness.models.response_instruction import MODEL_RESPONSE_INSTRUCTION
from harness.parser.response_parser import parse_model_response
from harness.providers.google_client import GeminiClient
from harness.mappers.google_mapper import (
    map_messages as google_messages,
    map_tool_schemas as google_tools,
)
from harness.providers.openai_client import OpenAIClient
from harness.mappers.openai_mapper import map_messages as openai_messages
from harness.tools.register_tools import register_tools
from harness.tools.tool_registry import ToolRegistry


class StructuredResponseAdaptersTest(unittest.TestCase):
    def test_gemini_requests_json_and_preserves_system_instruction(self):
        client = GeminiClient.__new__(GeminiClient)
        client._client = Mock()
        client._model = "test-model"
        client._client.models.generate_content.return_value = types.GenerateContentResponse(
            candidates=[types.Candidate(content=types.Content(parts=[types.Part.from_text(
                text='{"text":"Done","tool_calls":[],"tool_result_summaries":[]}'
            )]))]
        )
        self.assertEqual(client.generate([
            Message(role="system", content="Project instructions"),
            Message(role="user", content="Continue"),
        ]).text, "Done")
        config = client._client.models.generate_content.call_args.kwargs["config"]
        self.assertEqual(config.response_mime_type, "application/json")
        self.assertIsNone(config.tools)
        self.assertIn("Project instructions", config.system_instruction)
        self.assertIn(MODEL_RESPONSE_INSTRUCTION, config.system_instruction)

    def test_gemini_empty_response_reports_provider_reason(self):
        client = GeminiClient.__new__(GeminiClient)
        client._client = Mock()
        client._model = "test-model"
        cases = [
            (types.GenerateContentResponse(), "no response text"),
            (types.GenerateContentResponse(prompt_feedback={"block_reason": "SAFETY"}), "SAFETY"),
            (types.GenerateContentResponse(candidates=[types.Candidate(
                finish_reason="MAX_TOKENS"
            )]), "MAX_TOKENS"),
            (types.GenerateContentResponse(candidates=[types.Candidate(
                content=types.Content(parts=[types.Part.from_text(text="  \n")])
            )]), "no response text"),
        ]
        for response, reason in cases:
            with self.subTest(reason=reason):
                client._client.models.generate_content.return_value = response
                with self.assertRaisesRegex(ValueError, reason):
                    client.generate([Message(role="user", content="Continue")])

    def test_mappers_preserve_history_and_add_one_instruction(self):
        messages = [Message(role="system", content="Project instructions"),
                    Message(role="user", content="Read file"),
                    Message(role="assistant", content='Raw tool calls:\n[{"tool":"read_file"}]'),
                    Message(role="user", content="Tool result ID: original-id\nOutput:\ncontents")]
        contents, instruction = google_messages(messages)
        self.assertEqual(instruction.count(MODEL_RESPONSE_INSTRUCTION), 1)
        self.assertIn("Project instructions", instruction)
        self.assertEqual([c.role for c in contents], ["user", "model", "user"])
        self.assertEqual([c.parts[0].text for c in contents], [m.content for m in messages[1:]])
        mapped = openai_messages(messages)
        self.assertEqual(mapped[:-1], [{"role": m.role, "content": m.content} for m in messages])
        self.assertEqual(mapped[-1], {"role": "system", "content": MODEL_RESPONSE_INSTRUCTION})

    def test_gemini_does_not_extract_tools_from_system_text(self):
        catalog_text = (
            "Available tools:\n\n"
            "Tool: fake\nDescription: This is ordinary system content."
        )

        contents, instruction = google_messages([
            Message(role="system", content=catalog_text),
            Message(role="user", content="Continue"),
        ])

        self.assertEqual(google_tools([]), [])
        self.assertIn(catalog_text, instruction)
        self.assertEqual(contents[0].parts[0].text, "Continue")

    def test_gemini_rejects_unsupported_schema_constraints_explicitly(self):
        schemas = [{
            "name": "unsupported",
            "description": "Unsupported schema example.",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "string",
                        "unsupportedKeyword": True,
                    },
                },
                "required": ["value"],
                "additionalProperties": False,
            },
        }]

        with self.assertRaisesRegex(ValueError, "does not support"):
            google_tools(schemas)

    def test_gemini_receives_structured_native_tool_schemas(self):
        tool = Mock()
        tool.name = "example"
        tool.description = "Example tool."
        tool.arguments_schema = {
            "mode": {
                "type": "string",
                "enum": ["safe", "fast"],
            },
            "paths": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1,
            },
        }
        schemas = build_tools_schema([tool])
        client = GeminiClient.__new__(GeminiClient)
        client._client = Mock()
        client._model = "test-model"
        client._client.models.generate_content.return_value = (
            types.GenerateContentResponse(
                candidates=[
                    types.Candidate(
                        content=types.Content(
                            role="model",
                            parts=[
                                types.Part(
                                    function_call=types.FunctionCall(
                                        name="example",
                                        args={"mode": "safe", "paths": ["a"]},
                                    )
                                )
                            ],
                        )
                    )
                ]
            )
        )

        response = client.generate(
            [Message(role="user", content="Use the example tool")],
            schemas,
        )

        self.assertEqual(
            response.tool_calls,
            [
                ToolCall(
                    "example",
                    {"mode": "safe", "paths": ["a"]},
                )
            ],
        )
        config = client._client.models.generate_content.call_args.kwargs["config"]
        declaration = config.tools[0].function_declarations[0]
        self.assertEqual(declaration.name, "example")
        self.assertEqual(declaration.parameters.required, ["mode", "paths"])
        self.assertEqual(
            declaration.parameters.properties["mode"].enum,
            ["safe", "fast"],
        )
        self.assertEqual(
            declaration.parameters.properties["paths"].min_items,
            1,
        )

    def test_gemini_maps_all_registered_tools_and_complete_git_schema(self):
        registry = ToolRegistry()
        register_tools(registry)
        schemas = build_tools_schema(registry.list_tools())

        native_tools = google_tools(schemas)

        declarations = native_tools[0].function_declarations
        self.assertEqual(
            [declaration.name for declaration in declarations],
            [schema["name"] for schema in schemas],
        )
        git_declaration = next(
            declaration
            for declaration in declarations
            if declaration.name == "git"
        )
        command_name = git_declaration.parameters.properties["command_name"]
        command = git_declaration.parameters.properties["command"]
        self.assertIn("commit", command_name.enum)
        self.assertEqual(command.items.type, types.Type.STRING)
        self.assertGreater(command.max_items, 1)

    def test_adapters_return_contract_and_propagate_invalid_responses(self):
        raw = json.dumps(dict(text="", tool_calls=[dict(tool="read_file", arguments={"path": "a"}),
                                                   dict(tool="read_file", arguments={"path": "b"})],
                              tool_result_summaries=[dict(id="original-id", summary="Read previous file.")]))
        for cls in (GeminiClient, OpenAIClient):
            with self.subTest(provider=cls.__name__):
                client = cls.__new__(cls)
                client._client = Mock()
                client._model = "test-model"
                endpoint = (client._client.models.generate_content if cls is GeminiClient
                            else client._client.responses.create)
                if cls is GeminiClient:
                    endpoint.return_value = types.GenerateContentResponse(
                        candidates=[types.Candidate(content=types.Content(
                            parts=[types.Part.from_text(text=raw)]
                        ))]
                    )
                else:
                    endpoint.return_value = Mock(output_text=raw)
                self.assertEqual(client.generate([Message(role="user", content="Continue")]),
                                 parse_model_response(raw))
                if cls is GeminiClient:
                    endpoint.return_value = types.GenerateContentResponse(
                        candidates=[types.Candidate(content=types.Content(
                            parts=[types.Part.from_text(text="invalid")]
                        ))]
                    )
                else:
                    endpoint.return_value = Mock(output_text="invalid")
                with self.assertRaises(ValueError):
                    client.generate([Message(role="user", content="Continue")])
                endpoint.reset_mock()
                with self.assertRaises(ValueError):
                    client.generate([])
                endpoint.assert_not_called()
