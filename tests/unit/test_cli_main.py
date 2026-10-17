import io
import unittest
from unittest.mock import patch

from harness.app.cli.main import display_tool_result, main
from harness.domain.tool_result import ToolResult


class CliMainTest(unittest.TestCase):
    def test_main_processes_messages_until_exit(self) -> None:
        with (
            patch("harness.app.cli.main.load_dotenv"),
            patch("harness.app.cli.main.create_model_client") as create_model_client,
            patch("harness.app.cli.main.MainOrchestrator") as runner,
            patch("harness.app.cli.main.read_input", side_effect=["hello", "exit"]),
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            runner.return_value.handle.return_value = "Received: hello"
            main()

        runner.assert_called_once_with(
            model_client=create_model_client.return_value,
            on_tool_result=display_tool_result,
        )
        runner.return_value.handle.assert_called_once()
        self.assertEqual(runner.return_value.handle.call_args.args[0].message, "hello")
        self.assertEqual(
            stdout.getvalue(),
            "AI Harness started.\n"
            "Type 'exit' or 'quit' to stop.\n\n"
            "\nHarness > Received: hello\n\n"
            "AI Harness stopped.\n",
        )

    def test_main_stops_on_quit(self) -> None:
        with (
            patch("harness.app.cli.main.load_dotenv"),
            patch("harness.app.cli.main.create_model_client"),
            patch("harness.app.cli.main.MainOrchestrator") as runner,
            patch("harness.app.cli.main.read_input", return_value="quit"),
            patch("sys.stdout", new_callable=io.StringIO),
        ):
            main()

        runner.return_value.handle.assert_not_called()

    def test_display_tool_result_preserves_multiline_bash_output(self) -> None:
        result = ToolResult(
            name="bash",
            output="/project\n\ntotal 8\n-rw-r--r-- README.md",
        )

        with patch("sys.stdout", new_callable=io.StringIO) as stdout:
            display_tool_result(result)

        self.assertEqual(
            stdout.getvalue(),
            "\nTool [bash] completed:\n"
            "/project\n\n"
            "total 8\n"
            "-rw-r--r-- README.md\n",
        )

    def test_display_tool_result_identifies_failures(self) -> None:
        result = ToolResult(name="bash", output="permission denied", success=False)

        with patch("sys.stdout", new_callable=io.StringIO) as stdout:
            display_tool_result(result)

        self.assertEqual(
            stdout.getvalue(),
            "\nTool [bash] failed:\npermission denied\n",
        )

    def test_main_displays_multiple_tool_results_once_in_order(self) -> None:
        with (
            patch("harness.app.cli.main.load_dotenv"),
            patch("harness.app.cli.main.create_model_client"),
            patch("harness.app.cli.main.MainOrchestrator") as runner,
            patch("harness.app.cli.main.read_input", side_effect=["inspect", "exit"]),
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            def handle(_request):
                listener = runner.call_args.kwargs["on_tool_result"]
                listener(ToolResult("bash", "first output"))
                listener(ToolResult("read_file", "second output"))
                return "Done"

            runner.return_value.handle.side_effect = handle
            main()

        output = stdout.getvalue()
        first = "Tool [bash] completed:\nfirst output"
        second = "Tool [read_file] completed:\nsecond output"
        self.assertEqual(output.count(first), 1)
        self.assertEqual(output.count(second), 1)
        self.assertLess(output.index(first), output.index(second))


if __name__ == "__main__":
    unittest.main()
