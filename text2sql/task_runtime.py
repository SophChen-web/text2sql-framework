from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class TaskStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass
class AgentTask:
    question: str
    task_id: str = field(default_factory=lambda: str(uuid4()))
    status: TaskStatus = TaskStatus.QUEUED
    result: Any = None
    error: str | None = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

class TaskStore:
    """暂存在内存中的任务存储，服务重启后数据会清空。"""

    _ALLOWED_TRANSITIONS = {
        TaskStatus.QUEUED: {TaskStatus.RUNNING, TaskStatus.FAILED},
        TaskStatus.RUNNING: {TaskStatus.SUCCEEDED, TaskStatus.FAILED},
        TaskStatus.SUCCEEDED: set(),
        TaskStatus.FAILED: set(),
    }

    def __init__(self) -> None:
        self._tasks: dict[str, AgentTask] = {}

    def create(self, question: str) -> AgentTask:
        task = AgentTask(question=question)
        self._tasks[task.task_id] = task
        return task

    def get(self, task_id: str) -> AgentTask | None:
        return self._tasks.get(task_id)

    def set_status(
        self,
        task_id: str,
        status: TaskStatus,
        *,
        result: Any = None,
        error: str | None = None,
    ) -> AgentTask:
        task = self._tasks.get(task_id)
        if task is None:
            raise KeyError(f"Task not found: {task_id}")

        allowed = self._ALLOWED_TRANSITIONS[task.status]
        if status not in allowed:
            raise ValueError(
                f"Cannot change task from {task.status.value} to {status.value}"
            )

        task.status = status
        task.result = result
        task.error = error
        task.updated_at = datetime.now(timezone.utc)
        return task