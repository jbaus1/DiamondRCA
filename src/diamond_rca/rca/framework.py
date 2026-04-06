"""Orchestration scaffold for combining RCA artifacts."""

from dataclasses import dataclass, field
from pathlib import Path

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

    def to_markdown(self, title: str = "Diamond RCA Report") -> str:
        """Render the RCA report into Markdown for repeatable case-study deliverables."""
        return render_report_markdown(self, title=title)

    def save_markdown(self, path: str | Path, title: str = "Diamond RCA Report") -> Path:
        """Save the report as Markdown and return the destination path."""
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.to_markdown(title=title), encoding="utf-8")
        return output_path


def render_report_markdown(report: RCAReport, title: str = "Diamond RCA Report") -> str:
    """Generate a Markdown report from RCA artifacts.

    Parameters
    ----------
    report:
        Structured RCA report object.
    title:
        Heading shown at the top of the Markdown file.

    Returns
    -------
    str
        A complete Markdown document that can be committed, versioned, and shared.
    """
    lines: list[str] = [f"# {title}", "", "## Problem Statement", "", report.problem_statement, ""]

    lines.extend(["## 5 Whys", ""])
    if report.five_whys:
        for index, step in enumerate(report.five_whys, start=1):
            lines.append(f"{index}. **Question:** {step.question}")
            lines.append(f"   - **Answer:** {step.answer}")
    else:
        lines.append("No 5-whys entries were provided.")
    lines.append("")

    lines.extend(["## Fishbone", ""])
    if report.fishbone and report.fishbone.categories:
        lines.append(f"**Effect:** {report.fishbone.effect}")
        lines.append("")
        for category, causes in report.fishbone.categories.items():
            lines.append(f"### {category}")
            for cause in causes:
                lines.append(f"- {cause}")
            lines.append("")
    else:
        lines.append("No fishbone categories were provided.")
        lines.append("")

    lines.extend(["## Timeline", ""])
    if report.timeline:
        lines.extend(["| Date | Label | Description |", "|---|---|---|"])
        for event in sort_timeline(report.timeline):
            lines.append(
                f"| {event.event_date.isoformat()} | {event.label} | {event.description} |"
            )
    else:
        lines.append("No timeline events were provided.")

    lines.append("")
    return "\n".join(lines)
