"""Fishbone-style RCA scaffold."""

from dataclasses import dataclass, field


@dataclass
class Fishbone:
    """Simple fishbone structure keyed by category."""

    effect: str
    categories: dict[str, list[str]] = field(default_factory=dict)

    def add_cause(self, category: str, cause: str) -> None:
        """Append a cause under a fishbone category."""
        self.categories.setdefault(category, []).append(cause)


def default_categories() -> list[str]:
    """Return baseball-oriented default categories for fishbone analysis."""
    return [
        "Pitching",
        "Offense",
        "Defense",
        "Health",
        "Management",
        "Schedule/Opposition",
    ]
