"""Deterministic local task execution without network or source mutation."""

import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from typing import Iterable, List


@dataclass(frozen=True)
class TaskResult:
    """Result of processing one task on a local worker."""

    task_index: int
    node_id: int
    result: str


class LocalTaskRunner:
    """Run string tasks locally across a bounded pool of mock workers.

    This MVP deliberately has no network access, persistence, dynamic code
    loading, or source-code mutation. Results are returned in input order.
    """

    def __init__(self, worker_count: int = 3) -> None:
        if isinstance(worker_count, bool) or not isinstance(worker_count, int):
            raise TypeError("worker_count must be an integer")
        if worker_count < 1:
            raise ValueError("worker_count must be at least 1")
        self.worker_count = worker_count

    def run_tasks(self, tasks: Iterable[str]) -> List[TaskResult]:
        """Process tasks with local workers and return results in input order."""
        task_list = list(tasks)
        for index, task in enumerate(task_list):
            if not isinstance(task, str):
                raise TypeError("task at index {} must be a string".format(index))
            if not task.strip():
                raise ValueError("task at index {} must not be empty".format(index))

        if not task_list:
            return []

        with ThreadPoolExecutor(max_workers=self.worker_count) as executor:
            futures = [
                executor.submit(self._process, index, task)
                for index, task in enumerate(task_list)
            ]
            return [future.result() for future in futures]

    def _process(self, task_index: int, task: str) -> TaskResult:
        node_id = task_index % self.worker_count + 1
        return TaskResult(
            task_index=task_index,
            node_id=node_id,
            result="[Node-{}] Processed: {}".format(node_id, task),
        )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Run example tasks locally; no network or source mutation."
    )
    parser.add_argument(
        "--workers", type=int, default=3, help="number of local workers (default: 3)"
    )
    parser.add_argument(
        "--task",
        action="append",
        dest="tasks",
        help="task text; may be supplied more than once",
    )
    args = parser.parse_args(argv)
    tasks = args.tasks or ["example task"]

    try:
        results = LocalTaskRunner(args.workers).run_tasks(tasks)
    except (TypeError, ValueError) as error:
        parser.error(str(error))

    print(json.dumps([asdict(result) for result in results], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
