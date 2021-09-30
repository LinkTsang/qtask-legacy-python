import asyncio
import logging
from typing import List

from TaskScheduler import TaskScheduler
from schemas import TaskInfo
from utils import setup_logger


async def main(scheduler: TaskScheduler):
    logger = logging.getLogger('qtaskd')
    logger.info('running task scheduler...')

    try:
        demo_tasks: List[TaskInfo] = [
            TaskInfo(
                name="task 1",
                working_dir=".",
                command_line="python -m demo.task1",
                output_file_path="task1.output.log"
            ),
            TaskInfo(
                name="task 2",
                working_dir=".",
                command_line="python -m demo.task2",
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
    asyncio.run(main(TaskScheduler('./logs')))
