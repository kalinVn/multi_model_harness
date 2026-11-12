import json
from pathlib import Path

from harness.config.response.command_response_config import COMMAND_RESPONSE_FORMAT_INSTRUCTIONS
from harness.config.tool_usage_config import TOOL_USAGE_INSTRUCTIONS
from harness.domain.message import Message
from harness.domain.session import Session
from harness.tools.tool_registry import ToolRegistry


class SessionManager:
    def __init__(self, project_root: Path, tool_registry: ToolRegistry) -> None:
        self._project_root = project_root
        self._tool_registry = tool_registry

        self._sessions: dict[str, Session] = {}
        self._current_session_id: str | None = None

    @property
    def current_session(self) -> Session:
        if self._current_session_id is None:
            raise ValueError("No active session.")

        return self.get_session(self._current_session_id)

    def create_session(self) -> Session:
        system_prompt = self._load_system_prompt()
        system_context = (
            f"{system_prompt}\n\n"
            f"{TOOL_USAGE_INSTRUCTIONS}\n\n"
            f"{COMMAND_RESPONSE_FORMAT_INSTRUCTIONS}"
        )

        session = Session(
            messages=[
                Message(
                    role="system",
                    type="system_instruction",
                    content=system_context
                )
            ]
        )

        self._sessions[session.id] = session
        self._current_session_id = session.id

        return session

    def get_session(self, session_id: str) -> Session:
        session = self._sessions.get(session_id)

        if session is None:
            raise ValueError(f"Unknown session: {session_id}")

        return session

    def list_sessions(self) -> list[Session]:
        return list(self._sessions.values())

    def set_current_session(self, session_id: str) -> None:
        self.get_session(session_id)

        self._current_session_id = session_id

    def remove_session(self, session_id: str) -> None:
        self.get_session(session_id)

        del self._sessions[session_id]

        if self._current_session_id != session_id:
            return

        self._current_session_id = next(iter(self._sessions), None)

    def _load_system_prompt(self) -> str:
        system_prompt_path = self._project_root / ".caisa" / "CAISA.md"

        output = json.loads(
            self._tool_registry.execute(
                "read_file",
                {
                    "paths": [str(system_prompt_path)]
                }
            )
        )
        result = output["results"][0]
        if not result["success"]:
            raise RuntimeError(result["error"])
        return result["content"]
