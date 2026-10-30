import json
import unittest
from unittest.mock import Mock

from google.genai import types

from harness.builder.tool_parameters_builder import build_tool_parameters
from harness.config.response.gemini_response_instruction import (
    GEMINI_RESPONSE_INSTRUCTION,
)
from harness.converter.tool_converter_facade import ToolConverterFacade
from harness.domain.message import Message
from harness.domain.tool_call import ToolCall
from harness.models.response import ModelResponse
from harness.models.response_instruction import MODEL_RESPONSE_INSTRUCTION
from harness.parser.response_parser import prepare_model_response
from harness.providers.google_client import GeminiClient
from harness.mappers.google_mapper import (
    map_messages as google_messages,
    map_tool_definitions as google_tools,
)
from harness.providers.openai_client import OpenAIClient
from harness.mappers.openai_mapper import map_messages as openai_messages
from harness.tools.register_tools import register_tools
from harness.tools.tool_registry import ToolRegistry


class StructuredResponseAdaptersTest(unittest.TestCase):
    @staticmethod
    def gemini_response(text):
        return types.GenerateContentResponse(
            candidates=[types.Candidate(content=types.Content(
                parts=[types.Part.from_text(text=text)]
            ))]
        )

    def test_gemini_requests_plain_text_and_preserves_system_instruction(self):
        client = GeminiClient.__new__(GeminiClient)
        client._client = Mock()
        client._model = "test-model"
        client._tool_converter = ToolConverterFacade()
        client._client.models.generate_content.return_value = self.gemini_response("Done")
        self.assertEqual(client.generate([
            Message(role="system", content="Project instructions"),
            Message(role="user", content="Continue"),
        ]).text, "Done")
        config = client._client.models.generate_content.call_args.kwargs["config"]
        self.assertNotIn("response_mime_type", config)
        self.assertIsNone(config["tools"])
        self.assertIn("Project instructions", config["system_instruction"])
        self.assertIn(GEMINI_RESPONSE_INSTRUCTION, config["system_instruction"])
        self.assertIn(
            "respond with only the user-facing",
            config["system_instruction"],
        )

    def test_gemini_empty_response_reports_provider_reason(self):
        client = GeminiClient.__new__(GeminiClient)
        client._client = Mock()
        client._model = "test-model"
        client._tool_converter = ToolConverterFacade()
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

    def test_gemini_accepts_plain_text_answer(self):
        client = GeminiClient.__new__(GeminiClient)
        client._client = Mock()
        client._model = "test-model"
        client._tool_converter = ToolConverterFacade()
        client._client.models.generate_content.return_value = self.gemini_response(
            "136."
        )

        response = client.generate([
            Message(role="user", content="Колко е 17 по 8? Не използвай инструменти."),
        ])

        self.assertEqual(response, ModelResponse(text="136."))
        client._client.models.generate_content.assert_called_once()

    def test_gemini_returns_plain_text_for_hi_while_tools_remain_available(self):
        tool = Mock()
        tool.name = "example"
        tool.description = "Example tool."
        tool.get_parameter_object.return_value = {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        }
        schemas = build_tool_parameters([tool])
        client = GeminiClient.__new__(GeminiClient)
        client._client = Mock()
        client._model = "test-model"
        client._tool_converter = ToolConverterFacade()
        client._client.models.generate_content.return_value = self.gemini_response(
            "Hi! How can I help?"
        )

        response = client.generate([Message(role="user", content="hi")], schemas)

        self.assertEqual(response, ModelResponse(text="Hi! How can I help?"))
        config = client._client.models.generate_content.call_args.kwargs["config"]
        self.assertNotIn("response_mime_type", config)
        self.assertIsNotNone(config["tools"])

    def test_gemini_preserves_command_specific_json_without_outer_envelope(self):
        client = GeminiClient.__new__(GeminiClient)
        client._client = Mock()
        client._model = "test-model"
        client._tool_converter = ToolConverterFacade()
        command_response = '{"answer":"Done","command_summary":"Completed."}'
        client._client.models.generate_content.return_value = self.gemini_response(
            command_response
        )

        response = client.generate([Message(role="user", content="Run command")])

        self.assertEqual(response, ModelResponse(text=command_response))
        client._client.models.generate_content.assert_called_once()

    def test_gemini_hides_metadata_envelope_when_tool_calls_is_omitted(self):
        client = GeminiClient.__new__(GeminiClient)
        client._client = Mock()
        client._model = "test-model"
        client._tool_converter = ToolConverterFacade()
        raw = json.dumps({
            "text": "Файлът беше прочетен успешно.",
            "tool_result_summaries": [
                {"id": "result-1", "summary": "Прочетен е файлът."},
            ],
        })
        client._client.models.generate_content.return_value = (
            self.gemini_response(raw)
        )

        response = client.generate([Message(role="user", content="Read file")])

        self.assertEqual(response.text, "Файлът беше прочетен успешно.")
        self.assertEqual(response.tool_calls, [])
        self.assertEqual(response.tool_result_summaries[0].id, "result-1")

    def test_mappers_preserve_history_and_add_one_instruction(self):
        messages = [Message(role="system", content="Project instructions"),
                    Message(role="user", content="Read file"),
                    Message(role="assistant", content='Raw tool calls:\n[{"tool":"read_file"}]'),
                    Message(role="user", content="Tool result ID: original-id\nOutput:\ncontents")]
        contents, instruction = google_messages(messages)
        self.assertEqual(instruction.count(GEMINI_RESPONSE_INSTRUCTION), 1)
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

    def test_gemini_passes_json_schema_keywords_to_sdk(self):
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
        client = GeminiClient.__new__(GeminiClient)
        client._client = Mock()
        client._model = "test-model"
        client._tool_converter = ToolConverterFacade()
        client._client.models.generate_content.return_value = self.gemini_response(
            "Done"
        )

        client.generate(
            [Message(role="user", content="Use the unsupported tool")],
            schemas,
        )

        config = client._client.models.generate_content.call_args.kwargs["config"]
        schema = config["tools"][0]["function_declarations"][0][
            "parameters_json_schema"
        ]
        self.assertTrue(
            schema["properties"]["value"]["unsupportedKeyword"]
        )

    def test_gemini_receives_structured_native_tool_definitions(self):
        tool = Mock()
        tool.name = "example"
        tool.description = "Example tool."
        tool.get_parameter_object.return_value = {
            "type": "object",
            "properties": {
                "mode": {
                    "type": "string",
                    "description": "Execution mode.",
                    "enum": ["safe", "fast"],
                },
                "paths": {
                    "type": "array",
                    "description": "Paths to process.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                        },
                        "required": ["path"],
                        "additionalProperties": False,
                    },
                    "minItems": 1,
                },
            },
            "required": ["mode", "paths"],
            "additionalProperties": False,
        }
        schemas = build_tool_parameters([tool])
        client = GeminiClient.__new__(GeminiClient)
        client._client = Mock()
        client._model = "test-model"
        client._tool_converter = ToolConverterFacade()
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
                                        args={
                                            "mode": "safe",
                                            "paths": [{"path": "a"}],
                                        },
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
                    {"mode": "safe", "paths": [{"path": "a"}]},
                )
            ],
        )
        config = client._client.models.generate_content.call_args.kwargs["config"]
        declaration = config["tools"][0]["function_declarations"][0]
        self.assertEqual(declaration["name"], "example")
        self.assertNotIn("parameters", declaration)
        self.assertEqual(
            declaration["parameters_json_schema"],
            schemas[0]["parameters"],
        )
        self.assertFalse(declaration["parameters_json_schema"]["additionalProperties"])
        nested_items = declaration["parameters_json_schema"]["properties"][
            "paths"
        ]["items"]
        self.assertFalse(nested_items["additionalProperties"])
        self.assertEqual(
            declaration["parameters_json_schema"]["properties"]["mode"]["enum"],
            ["safe", "fast"],
        )
        self.assertEqual(
            declaration["parameters_json_schema"]["properties"]["paths"]["minItems"],
            1,
        )

    def test_gemini_maps_all_registered_tools_and_complete_git_schema(self):
        registry = ToolRegistry()
        register_tools(registry)
        schemas = build_tool_parameters(registry.list_tools())

        native_tools = google_tools(schemas)

        declarations = native_tools[0]["function_declarations"]
        self.assertEqual(
            [declaration["name"] for declaration in declarations],
            [schema["name"] for schema in schemas],
        )
        git_declaration = next(
            declaration
            for declaration in declarations
            if declaration["name"] == "git"
        )
        parameters = git_declaration["parameters_json_schema"]
        command_name = parameters["properties"]["command_name"]
        command = parameters["properties"]["command"]
        self.assertIn("commit", command_name["enum"])
        self.assertEqual(command["items"]["type"], "string")
        self.assertGreater(command["maxItems"], 1)

    def test_adapters_return_contract_and_propagate_invalid_responses(self):
        raw = json.dumps(dict(text="Done", tool_calls=[],
                              tool_result_summaries=[dict(id="original-id", summary="Read previous file.")]))
        for cls in (GeminiClient, OpenAIClient):
            with self.subTest(provider=cls.__name__):
                client = cls.__new__(cls)
                client._client = Mock()
                client._model = "test-model"
                if cls is GeminiClient:
                    client._tool_converter = ToolConverterFacade()
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
                                 prepare_model_response(raw))
                if cls is GeminiClient:
                    endpoint.return_value = types.GenerateContentResponse(
                        candidates=[types.Candidate(content=types.Content(
                            parts=[types.Part.from_text(text="invalid")]
                        ))]
                    )
                else:
                    endpoint.return_value = Mock(output_text="invalid")
                if cls is GeminiClient:
                    self.assertEqual(
                        client.generate([Message(role="user", content="Continue")]),
                        ModelResponse(text="invalid"),
                    )
                else:
                    with self.assertRaises(ValueError):
                        client.generate([Message(role="user", content="Continue")])
                endpoint.reset_mock()
                with self.assertRaises(ValueError):
                    client.generate([])
                endpoint.assert_not_called()
