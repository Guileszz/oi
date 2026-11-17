"""Safe, local-only task runner MVP for the oi project."""

from .runner import LocalTaskRunner, TaskResult

__all__ = ["LocalTaskRunner", "TaskResult"]
