"""Orchestration scaffold for combining RCA artifacts."""

from dataclasses import dataclass, field

from diamond_rca.rca.fishbone import Fishbone
from diamond_rca.rca.five_whys import WhyStep
from diamond_rca.rca.timeline import TimelineEvent, sort_timeline


@dataclass
class RCAReport:
    """Container for structured RCA outputs."""

    problem_statement: str
    five_whys: list[WhyStep] = field(default_factory=list)
    fishbone: Fishbone | None = None
    timeline: list[TimelineEvent] = field(default_factory=list)

    def add_timeline_events(self, events: list[TimelineEvent]) -> None:
        """Add and sort timeline events."""
        self.timeline.extend(events)
        self.timeline = sort_timeline(self.timeline)
