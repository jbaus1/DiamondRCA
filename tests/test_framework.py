from datetime import date

from diamond_rca.rca.fishbone import Fishbone
from diamond_rca.rca.five_whys import WhyStep
from diamond_rca.rca.framework import RCAReport
from diamond_rca.rca.timeline import TimelineEvent


def test_rca_report_to_markdown_and_save(tmp_path):
    report = RCAReport(
        problem_statement="The Mets posted a prolonged losing stretch in late season.",
        five_whys=[
            WhyStep(question="Why did the team lose?", answer="Bullpen run prevention declined."),
            WhyStep(
                question="Why did bullpen run prevention decline?",
                answer="High leverage relievers were overused.",
            ),
        ],
        fishbone=Fishbone(effect="Sustained decline in win rate"),
    )
    report.fishbone.add_cause("Pitching", "Late-inning command inconsistency")
    report.add_timeline_events(
        [
            TimelineEvent(date(2025, 7, 15), "Injury", "Key reliever placed on IL"),
            TimelineEvent(date(2025, 8, 5), "Skid", "Losing streak reached 6 games"),
        ]
    )

    markdown = report.to_markdown(title="2025 Mets Collapse RCA")

    assert "# 2025 Mets Collapse RCA" in markdown
    assert "## 5 Whys" in markdown
    assert "## Fishbone" in markdown
    assert "## Timeline" in markdown

    output_path = report.save_markdown(
        tmp_path / "mets_2025_rca.md", title="2025 Mets Collapse RCA"
    )

    assert output_path.exists()
    assert "2025-07-15" in output_path.read_text(encoding="utf-8")
