from pathlib import Path

from harness.tools.read_file_tool import (
    ReadFileTool,
)
from harness.tools.write_file_tool import (
    WriteFileTool,
)
from harness.tools.bash_tool import (
    BashTool,
)
from harness.tools.tool_registry import (
    ToolRegistry,
)


def register_tools(
    registry: ToolRegistry,
    working_directory: Path | None = None,
) -> None:
    registry.register(ReadFileTool())

    registry.register(WriteFileTool())

    registry.register(BashTool(working_directory=working_directory))
