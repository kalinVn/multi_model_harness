from dotenv import load_dotenv

from harness.agents.main_orchestrator import MainOrchestrator
from harness.app.cli.reader import read_input
from harness.domain.tool_result import ToolResult
from harness.factory.model_client_factory import create_model_client
from harness.models.errors import (
    ModelConnectionError,
    ModelRateLimitError,
)
from harness.models.request import Request


def display_tool_result(tool_result: ToolResult) -> None:
    status = "completed" if tool_result.success else "failed"
    print(f"\nTool [{tool_result.name}] {status}:\n{tool_result.output}", flush=True)


def main() -> None:
    load_dotenv()

    print("AI Harness started.")
    print("Type 'exit' or 'quit' to stop.\n")

    model_client = create_model_client()
    runner = MainOrchestrator(
        model_client=model_client,
        on_tool_result=display_tool_result,
    )

    while True:
        user_message = read_input()

        if user_message.lower() in {"exit", "quit"}:
            print("AI Harness stopped.")
            break

        request = Request.create(user_message)

        try:
            response = runner.handle(request)
        except (
            ModelConnectionError,
            ModelRateLimitError,
        ) as error:
            print(f"\nHarness > {error}\n")
            continue

        print(f"\nHarness > {response}\n")


if __name__ == "__main__":
    main()
