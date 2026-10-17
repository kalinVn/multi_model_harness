import os
from pathlib import Path

from harness.config.git_tool_config import (
    GIT_REMOTE_OPERATIONS_ENVIRONMENT_VARIABLE,
    GIT_WRITE_OPERATIONS_ENVIRONMENT_VARIABLE,
)
from harness.tools.read_file_tool import (
    ReadFileTool,
)
from harness.tools.write_file_tool import (
    WriteFileTool,
)
from harness.tools.bash_tool import (
    BashTool,
)
from harness.tools.git_tool import GitTool
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

    allow_git_write_operations = (
        os.getenv(GIT_WRITE_OPERATIONS_ENVIRONMENT_VARIABLE, "").strip().lower()
        == "true"
    )
    allow_git_remote_operations = (
        os.getenv(GIT_REMOTE_OPERATIONS_ENVIRONMENT_VARIABLE, "").strip().lower()
        == "true"
    )
    registry.register(
        GitTool(
            working_directory=working_directory,
            allow_write_operations=allow_git_write_operations,
            allow_remote_operations=allow_git_remote_operations,
        )
    )
