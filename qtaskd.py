import asyncio
import logging
from typing import List

from config import QTASK_DATABASE_URL
from qtask_ctrld import TaskControlDaemon
from schemas import TaskInfo
from store import StoreDB
from utils import setup_logger, setup_data_dirs


async def main(task_control_daemon: TaskControlDaemon):
    logger = logging.getLogger('qtaskd')
    logger.info('running task scheduler...')

    try:
        demo_tasks: List[TaskInfo] = [
            TaskInfo(
                name="6s task",
                working_dir=".",
                command_line="python -m demo.dummy_task -t 6",
                output_file_path="task6.output.log"
            ),
            TaskInfo(
                name="2s task",
                working_dir=".",
                command_line="python -m demo.dummy_task -t 2",
                output_file_path="task2.output.log"
            ),
        ]

        task_control_daemon.init_asyncio()
        scheduler_task = asyncio.create_task(task_control_daemon.run())

        for t in demo_tasks:
            task_control_daemon.add_task(t)

        await scheduler_task

    except Exception:
        logger.exception('task scheduler uncaught exception')

    logger.info('task scheduler exited.')


if __name__ == "__main__":
    setup_data_dirs()
    setup_logger()
    scheduler = TaskControlDaemon(StoreDB(QTASK_DATABASE_URL), './logs')
    asyncio.run(main(scheduler))
