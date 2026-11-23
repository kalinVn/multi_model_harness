from dataclasses import asdict, dataclass, field
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class ImportantToolFinding:
    tool_execution_id: str | None
    tool_name: str
    agent_id: str | None
    finding: str


@dataclass(frozen=True)
class ContextMemorySummary:
    summary_id: str
    session_id: str
    version: int
    current_goal: str | None = None
    conversation_summary: str = ""
    decisions: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    important_tool_findings: list[ImportantToolFinding] = field(default_factory=list)
    important_files: list[str] = field(default_factory=list)
    current_state: str = ""
    pending_steps: list[str] = field(default_factory=list)
    active_plan_id: str | None = None

    @classmethod
    def empty(cls, session_id: str) -> "ContextMemorySummary":
        return cls(summary_id=str(uuid4()), session_id=session_id, version=1)

    @classmethod
    def from_model_data(
        cls,
        data: dict[str, Any],
        session_id: str,
        version: int,
        summary_id: str | None = None
    ) -> "ContextMemorySummary":
        expected_fields = {
            "current_goal",
            "conversation_summary",
            "decisions",
            "constraints",
            "important_tool_findings",
            "important_files",
            "current_state",
            "pending_steps",
            "active_plan_id"
        }
        if not isinstance(data, dict) or set(data) != expected_fields:
            raise ValueError("Context memory response contains invalid fields.")

        cls._validate_optional_string(data["current_goal"], "current_goal")
        cls._validate_string(data["conversation_summary"], "conversation_summary")
        cls._validate_string_list(data["decisions"], "decisions")
        cls._validate_string_list(data["constraints"], "constraints")
        cls._validate_string_list(data["important_files"], "important_files")
        cls._validate_string(data["current_state"], "current_state")
        cls._validate_string_list(data["pending_steps"], "pending_steps")
        cls._validate_optional_string(data["active_plan_id"], "active_plan_id")

        findings = cls._parse_findings(data["important_tool_findings"])

        return cls(
            summary_id=summary_id or str(uuid4()),
            session_id=session_id,
            version=version,
            current_goal=data["current_goal"],
            conversation_summary=data["conversation_summary"],
            decisions=data["decisions"],
            constraints=data["constraints"],
            important_tool_findings=findings,
            important_files=data["important_files"],
            current_state=data["current_state"],
            pending_steps=data["pending_steps"],
            active_plan_id=data["active_plan_id"]
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def _parse_findings(value: Any) -> list[ImportantToolFinding]:
        if not isinstance(value, list):
            raise ValueError("important_tool_findings must be a list.")

        expected_fields = {"tool_execution_id", "tool_name", "agent_id", "finding"}
        findings = []
        seen_findings = set()
        for item in value:
            if not isinstance(item, dict) or set(item) != expected_fields:
                raise ValueError("Important tool finding contains invalid fields.")

            ContextMemorySummary._validate_optional_string(item["tool_execution_id"], "tool_execution_id")
            ContextMemorySummary._validate_string(item["tool_name"], "tool_name", nonempty=True)
            ContextMemorySummary._validate_optional_string(item["agent_id"], "agent_id")
            ContextMemorySummary._validate_string(item["finding"], "finding", nonempty=True)

            finding_key = tuple(item[field] for field in sorted(expected_fields))
            if finding_key in seen_findings:
                continue

            seen_findings.add(finding_key)
            findings.append(ImportantToolFinding(**item))

        return findings

    @staticmethod
    def _validate_string(value: Any, field_name: str, nonempty: bool = False) -> None:
        if not isinstance(value, str) or nonempty and not value.strip():
            raise ValueError(f"{field_name} must be a string.")

    @staticmethod
    def _validate_optional_string(value: Any, field_name: str) -> None:
        if value is not None and not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string or null.")

    @staticmethod
    def _validate_string_list(value: Any, field_name: str) -> None:
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            raise ValueError(f"{field_name} must be a list of strings.")
