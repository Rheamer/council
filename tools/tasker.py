"""Pseudo task-manager API.

Tasks live in ``data/tasker.json`` under a top-level ``"tasks"`` key. Each
task carries its subtasks inline in the file, but the API deliberately
exposes them *separately*: you must list tasks first, then call
:func:`get_subtasks` once per task to fetch its children.

Design intent: sequential / hierarchical tool calling.

This mock imitates a real external service, so it is **deliberately flaky**:
every public call has a 5% chance of raising :class:`TaskerServiceError`, the
way a real network API throws transient 5xx / timeout errors. Wrap this API
with retry / error handling -- a call that fails will usually succeed on retry.
"""

from __future__ import annotations

import json
import random
from functools import lru_cache
from pathlib import Path

_TASKER_PATH = Path(__file__).resolve().parent.parent / "data" / "tasker.json"

_FAILURE_RATE = 0.05


class TaskerServiceError(RuntimeError):
    """Simulated transient failure from the (mock) external task service.

    Treat this like a 503 / timeout from a real API: it is intermittent and
    typically resolves if you retry the call.
    """


def _maybe_fail() -> None:
    """Randomly raise to imitate a flaky external service. Called per request."""
    if random.random() < _FAILURE_RATE:
        raise TaskerServiceError(
            "Task service temporarily unavailable (simulated 503). Please retry."
        )


@lru_cache(maxsize=1)
def _load() -> list[dict]:
    with _TASKER_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)["tasks"]


def get_tasks() -> list[dict]:
    """Return top-level tasks only (no subtasks)::

        [{"task_id": "t_001", "title": "...", "status": "in_progress",
          "due_date": "2024-09-01"}, ...]

    May raise :class:`TaskerServiceError` (transient -- retry).
    """
    _maybe_fail()
    return [
        {
            "task_id": t["task_id"],
            "title": t["title"],
            "status": t["status"],
            "due_date": t["due_date"],
        }
        for t in _load()
    ]


def get_subtasks(task_id: str) -> list[dict]:
    """Return subtasks for one task. Must be called once per parent task::

        [{"subtask_id": "s_001", "title": "...", "status": "...",
          "due_date": "..."}, ...]

    May raise :class:`TaskerServiceError` (transient -- retry).
    Raises ``KeyError`` if the task does not exist.
    """
    _maybe_fail()
    for task in _load():
        if task["task_id"] == task_id:
            return [dict(s) for s in task.get("subtasks", [])]
    raise KeyError(f"Unknown task_id: {task_id!r}")


def get_task_details(task_id: str) -> dict:
    """Return the full task object with description and notes (no subtasks).

    May raise :class:`TaskerServiceError` (transient -- retry).
    Raises ``KeyError`` if the task does not exist.
    """
    _maybe_fail()
    for task in _load():
        if task["task_id"] == task_id:
            return {
                "task_id": task["task_id"],
                "title": task["title"],
                "status": task["status"],
                "due_date": task["due_date"],
                "description": task.get("description", ""),
                "notes": task.get("notes", ""),
            }
    raise KeyError(f"Unknown task_id: {task_id!r}")
