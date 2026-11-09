from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

@dataclass
class TraceEvent:
    node: str
    status: str
    started_at: str
    duration_ms: int
    input_summary: dict[str, Any] = field(default_factory=dict)
    output_summary: dict[str, Any] = field(default_factory=dict)

class TraceCollector:
    def __init__(self, trace_id: str | None = None):
        self.trace_id = trace_id or f"trace_{uuid4().hex[:12]}"
        self.events: list[TraceEvent] = []

    def add(self, node: str, duration_ms: int, *, status: str = "success",
            input_summary: dict[str, Any] | None = None,
            output_summary: dict[str, Any] | None = None) -> None:
        self.events.append(
            TraceEvent(
                node=node,
                status=status,
                started_at=datetime.now(timezone.utc).isoformat(),
                duration_ms=duration_ms,
                input_summary=input_summary or {},
                output_summary=output_summary or {},
            )
        )

    def to_dict(self) -> dict[str, Any]:
        return {"trace_id": self.trace_id, "events": [event.__dict__ for event in self.events]}
