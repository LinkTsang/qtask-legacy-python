import unittest

from qtask.executor import Executor
from qtask.schemas import TaskInfo, TaskStatus
from qtask.utils.testing import async_test


class ExecutorTestCase(unittest.TestCase):
    @async_test
    async def test_run_task(self):
        dummy_task = TaskInfo(
            name="1s task",
            status=TaskStatus.READY,
            working_dir="",
            command_line="python -m demo.dummy_task -t 1",
            output_file_path="task1.output.log",
        )

        task_done_flag = False

        def handle_task_status_changed(task: TaskInfo):
            nonlocal task_done_flag
            task_done_flag = True

            self.assertEqual(dummy_task.id, task.id)
            self.assertEqual(TaskStatus.COMPLETED, task.status)

        executor = Executor()
        executor._status_changed.on(handle_task_status_changed)

        self.assertFalse(task_done_flag)

        await executor.run_task(dummy_task)

        self.assertTrue(task_done_flag)


if __name__ == '__main__':
    unittest.main()
