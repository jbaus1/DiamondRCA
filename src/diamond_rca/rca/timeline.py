"""Timeline utilities for RCA event sequencing."""

from dataclasses import dataclass
from datetime import date


@dataclass
class TimelineEvent:
    """A dated event relevant to collapse analysis."""

    event_date: date
    label: str
    description: str


def sort_timeline(events: list[TimelineEvent]) -> list[TimelineEvent]:
    """Sort events by date ascending."""
    return sorted(events, key=lambda e: e.event_date)
