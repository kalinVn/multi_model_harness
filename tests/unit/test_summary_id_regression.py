import json
import unittest
from unittest.mock import Mock, patch

from harness.agents.main_orchestrator import MainOrchestrator
from harness.builder.command_response_format_context_builder import build_command_response_format_context
from harness.session_manager import SessionManager
from harness.models.request import Request
from harness.domain.message import Message
from harness.domain.tool_result import ToolResult
from harness.parser.command_response_parser import parse_command_response
from harness.parser.response_parser import prepare_model_response


class SummaryIDRegressionTest(unittest.TestCase):
    def test_original_ids_match_across_messages_before_new_execution(self):
        ids = ["bc950638-61a9-4662-a330-76c77c43225d", "99f97142-ae4f-404f-a0f5-81a998a42df6"]
        results = [ToolResult("read_file", f"raw {i}", id=id_) for i, id_ in enumerate(ids)]
        payload = dict(text="", tool_calls=[dict(tool="read_file", arguments={"paths": ["next"]})],
                       tool_result_summaries=[dict(id=ids[1], summary="second"),
                                              dict(id="future-id", summary="invented"),
                                              dict(id=ids[0], summary="first")])
        client = Mock()
        client.generate.side_effect = [prepare_model_response(json.dumps(payload)),
            prepare_model_response(json.dumps(dict(text="Done", tool_calls=[], tool_result_summaries=[])))]
        with patch.object(SessionManager, "_load_system_prompt", return_value="Instructions"):
            runner = MainOrchestrator(client)
        session = runner._session_manager.current_session
        for result in results:
            session.add_message(Message(role="user", content=result.output, tool_results=(result,)))

        def execute(*args):
            self.assertEqual([r.summary for r in results], ["first", "second"])
            self.assertEqual(sum(len(m.tool_results) for m in session.messages), 2)
            return "new output"

        runner._tool_registry.execute = Mock(side_effect=execute)
        with patch("harness.domain.tool_result.uuid4", return_value="future-id"):
            self.assertEqual(runner.handle(Request.create("Continue")), "Done")
        stored = [r for m in session.messages for r in m.tool_results]
        self.assertEqual([r.id for r in stored], ids + ["future-id"])
        self.assertEqual([r.summary for r in stored], ["first", "second", ""])
        self.assertEqual([r.output for r in results], ["raw 0", "raw 1"])

    def test_command_json_stays_inside_text(self):
        inner = json.dumps(dict(answer="Done", command_summary="Reviewed files."))
        response = prepare_model_response(json.dumps(dict(text=inner, tool_calls=[], tool_result_summaries=[])))
        self.assertEqual(
            parse_command_response(response.text),
            ("Done", "Reviewed files."),
        )
        instruction = build_command_response_format_context().content
        self.assertIn("`text` string", instruction)
        self.assertIn("`tool_result_summaries`", instruction)
