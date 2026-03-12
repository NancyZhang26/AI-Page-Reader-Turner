from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(slots=True)
class TurnPageSignal:
    source: str
    reason: str
    timestamp_iso: str


class SoftwareProtocolBus:
    """Placeholder protocol bus used before hardware integration exists."""

    def emit_turn_page(self, source: str, reason: str) -> TurnPageSignal:
        return TurnPageSignal(
            source=source,
            reason=reason,
            timestamp_iso=datetime.now(timezone.utc).isoformat(),
        )
