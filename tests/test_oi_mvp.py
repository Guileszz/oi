import unittest

from oi_mvp import LocalTaskRunner


class LocalTaskRunnerTests(unittest.TestCase):
    def test_processes_tasks_and_assigns_workers_round_robin(self):
        results = LocalTaskRunner(worker_count=2).run_tasks(["alpha", "beta", "gamma"])

        self.assertEqual([result.task_index for result in results], [0, 1, 2])
        self.assertEqual([result.node_id for result in results], [1, 2, 1])
        self.assertEqual(
            [result.result for result in results],
            [
                "[Node-1] Processed: alpha",
                "[Node-2] Processed: beta",
                "[Node-1] Processed: gamma",
            ],
        )

    def test_empty_task_list_returns_empty_results(self):
        self.assertEqual(LocalTaskRunner().run_tasks([]), [])

    def test_worker_count_must_be_positive(self):
        with self.assertRaises(ValueError):
            LocalTaskRunner(worker_count=0)

    def test_worker_count_must_be_integer(self):
        with self.assertRaises(TypeError):
            LocalTaskRunner(worker_count=1.5)

    def test_rejects_empty_task(self):
        with self.assertRaises(ValueError):
            LocalTaskRunner().run_tasks([" "])

    def test_rejects_non_string_task(self):
        with self.assertRaises(TypeError):
            LocalTaskRunner().run_tasks([123])


if __name__ == "__main__":
    unittest.main()
