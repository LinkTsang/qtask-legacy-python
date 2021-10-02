import unittest

from qtaskd import TaskDaemon
from schemas import TaskInfo, TaskStatus
from utils.testing import async_test


class TaskDaemonTestCase(unittest.TestCase):
    @async_test
    async def test_run_task(self):
        dummy_task = TaskInfo(
            name="1s task",
            status=TaskStatus.READY,
            working_dir=".",
            command_line="python -m demo.dummy_task -t 1",
            output_file_path="task1.output.log",
        )

        task_done_flag = False

        def handle_task_done(task: TaskInfo):
            nonlocal task_done_flag
            task_done_flag = True

            self.assertEqual(dummy_task.id, task.id)
            self.assertEqual(TaskStatus.COMPLETED, task.status)

        def handle_task_failed(task: TaskInfo):
            self.fail(msg='task failed %r' % task)

        task_daemon = TaskDaemon()
        task_daemon.task_done.on(handle_task_done)
        task_daemon.task_failed.on(handle_task_failed)

        self.assertFalse(task_done_flag)

        await task_daemon.run_task(dummy_task)

        self.assertTrue(task_done_flag)


if __name__ == '__main__':
    unittest.main()
