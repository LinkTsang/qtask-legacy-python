import asyncio
import logging
from typing import List

from TaskScheduler import TaskScheduler
from config import QTASK_DATABASE_URL
from schemas import TaskInfo
from store import StoreDB
from utils import setup_logger


async def main(scheduler: TaskScheduler):
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

        scheduler.init_asyncio()
        scheduler_task = asyncio.create_task(scheduler.run())

        for t in demo_tasks:
            scheduler.add_task(t)

        await scheduler_task

    except Exception:
        logger.exception('task scheduler uncaught exception')

    logger.info('task scheduler exited.')


if __name__ == "__main__":
    setup_logger()
    scheduler = TaskScheduler(StoreDB(QTASK_DATABASE_URL), './logs')
    asyncio.run(main(scheduler))
