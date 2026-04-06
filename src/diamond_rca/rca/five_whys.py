"""5 Whys RCA scaffold."""

from dataclasses import dataclass


@dataclass
class WhyStep:
    """A single why-question step."""

    question: str
    answer: str


def build_five_whys(problem_statement: str, answers: list[str]) -> list[WhyStep]:
    """Create a 5-Whys chain from a problem statement and answer list."""
    steps: list[WhyStep] = []
    current_question = f"Why did this happen? ({problem_statement})"
    for answer in answers[:5]:
        steps.append(WhyStep(question=current_question, answer=answer))
        current_question = f"Why? Because: {answer}"
    return steps
