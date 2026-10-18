from pathlib import Path

from harness.domain.message import Message
from harness.domain.session import Session
from harness.tools.tool_registry import (
    ToolRegistry,
)
from harness.builder.tools_schema_builder import (
    build_tools_context,
)


class SessionManager:
    def __init__(
        self,
        project_root: Path,
        tool_registry: ToolRegistry,
    ) -> None:
        self._project_root = project_root
        self._tool_registry = tool_registry

        self._sessions: dict[str, Session] = {}
        self._current_session_id: str | None = None

    @property
    def current_session(
        self,
    ) -> Session:
        if self._current_session_id is None:
            raise ValueError("No active session.")

        return self.get_session(self._current_session_id)

    def create_session(
        self,
    ) -> Session:
        system_prompt =  self._load_system_prompt()

        tools_context = self._build_tools_context()

        session = Session(
            messages=[
                Message(role="system", content=system_prompt),
                Message(role="system", content=tools_context),
            ]
        )

        self._sessions[session.id] = session
        self._current_session_id = session.id

        return session

    def get_session(
        self,
        session_id: str,
    ) -> Session:
        session = self._sessions.get(session_id)

        if session is None:
            raise ValueError(f"Unknown session: {session_id}")

        return session

    def list_sessions(
        self,
    ) -> list[Session]:
        return list(self._sessions.values())

    def set_current_session(
        self,
        session_id: str,
    ) -> None:
        self.get_session(session_id)

        self._current_session_id = session_id

    def remove_session(
        self,
        session_id: str,
    ) -> None:
        self.get_session(session_id)

        del self._sessions[session_id]

        if self._current_session_id != session_id:
            return

        self._current_session_id = next(iter(self._sessions), None)

    def _load_system_prompt(
        self,
    ) -> str:
        system_prompt_path = (
            self._project_root
            / ".caisa"
            / "CAISA.md"
        )

        return self._tool_registry.execute(
            "read_file",
            {
                "path": str(system_prompt_path),
            },
        )

    def _build_tools_context(
        self,
    ) -> str:
        
        tools = self._tool_registry.list_tools()

        return build_tools_context(tools)
