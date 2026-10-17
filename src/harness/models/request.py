from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class Request:
    message: str
    created_at: datetime

    @classmethod
    def create(cls, message: str) -> "Request":
        return cls(message=message, created_at=datetime.now(timezone.utc))
