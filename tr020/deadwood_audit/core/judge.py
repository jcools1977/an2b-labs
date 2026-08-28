"""The quality judge (DECISIONS D15): fixed rubric, 1-10, greedy,
disjoint from the actor model. Must pass the D3 damage gate (with
human-ratified fixtures, D13) before any delta it produces counts.
"""
import re

RUBRIC = (
    "You are grading the quality of a system's final answer to a task. "
    "Score 1-10 where 10 is a complete, correct, on-task answer and 1 is "
    "useless or off-topic. Judge only quality; wording style does not "
    "matter. Reply with the integer score only.\n\n"
    "Task: {task}\nAnswer: {answer}\nScore:"
)


class Judge:
    def __init__(self, lm):
        self.lm = lm

    def score(self, task, answer, seed):
        out = self.lm.generate(
            RUBRIC.format(task=task, answer=answer), seed=seed, max_tokens=8
        )
        m = re.search(r"\b([1-9]|10)\b", out)
        return int(m.group(1)) if m else None  # None = judge error, never imputed
