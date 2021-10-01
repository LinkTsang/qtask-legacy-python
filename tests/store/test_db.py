import unittest

from config import QTASK_DATABASE_URL
from schemas import TaskInfo, TaskStatus
from store import StoreDB
from utils import setup_data_dirs


class StoreDBTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        setup_data_dirs()

    def test_tasks(self):
        store = StoreDB(QTASK_DATABASE_URL)
        task1 = TaskInfo(
            name="6s task",
            working_dir=".",
            command_line="python -m demo.dummy_task -t 6",
            output_file_path="task6.output.log"
        )
        task2 = TaskInfo(
            name="2s task",
            working_dir=".",
            command_line="python -m demo.dummy_task -t 2",
            output_file_path="task2.output.log"
        )

        store.enqueue_task(task1)
        store.enqueue_task(task2)

        task1_db = store.get_task_by_id(task1.id)
        task2_db = store.get_task_by_id(task2.id)
        self.assertEqual(task1_db, task1)
        self.assertEqual(task2_db, task2)

        self.assertTrue(store.exists_pending_tasks())

        task = store.dequeue_task()
        self.assertEqual(task.status, TaskStatus.READY)

        store.update_task_status_by_id(task1.id, TaskStatus.CANCELED)
        store.update_task_status_by_id(task2.id, TaskStatus.CANCELED)

        task1_db = store.get_task_by_id(task1.id)
        task2_db = store.get_task_by_id(task2.id)

        self.assertEqual(task1_db.status, TaskStatus.CANCELED)
        self.assertEqual(task2_db.status, TaskStatus.CANCELED)


if __name__ == '__main__':
    unittest.main()
