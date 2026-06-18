from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


COLLECT_FUNGUS_SAMPLE = "collect_fungus_sample"
ANALYZE_FUNGUS_SAMPLE = "analyze_fungus_sample"


@dataclass(frozen=True)
class QuestStep:
    id: str
    title: str
    objective: str
    xp: int


BIOLOGY_STEPS = [
    QuestStep(
        id=COLLECT_FUNGUS_SAMPLE,
        title="Collect a fungus sample",
        objective="Go north to the Fungus Grove and collect the fungus sample.",
        xp=10,
    ),
    QuestStep(
        id=ANALYZE_FUNGUS_SAMPLE,
        title="Analyze the sample",
        objective="Bring the fungus sample to the Microscope Tent and use the microscope.",
        xp=20,
    ),
]


def active_objective(completed_tasks: set[str]) -> str:
    for step in BIOLOGY_STEPS:
        if step.id not in completed_tasks:
            return step.objective
    return "Report your findings to Dr. Lin. Biology Realm quest complete."


def quest_summary(completed_tasks: set[str]) -> str:
    finished = sum(1 for step in BIOLOGY_STEPS if step.id in completed_tasks)
    return f"Biology Investigation {finished}/{len(BIOLOGY_STEPS)}: {active_objective(completed_tasks)}"


def step_for_task(task_id: str) -> Optional[QuestStep]:
    for step in BIOLOGY_STEPS:
        if step.id == task_id:
            return step
    return None
