from pathlib import Path


class CommandResolver:
    def __init__(self, commands_directory: Path) -> None:
        self._commands_directory = commands_directory

    def resolve(self, command_name: str) -> Path:
        """Check whether the command file exists.

        The command name is provided as an argument, while the resolver stores
        the commands directory.
        """
        command_path = (
            self._commands_directory
            / f"{command_name}.md"
        )

        if not command_path.is_file():
            raise ValueError(
                f"Unknown command: {command_name}"
            )
        
        return command_path
