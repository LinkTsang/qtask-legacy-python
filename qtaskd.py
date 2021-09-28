import asyncio
from typing import List

from TaskScheduler import TaskScheduler
from model import TaskInfo


async def demo():
    tasks: List[TaskInfo] = [
        TaskInfo(
            name="task 1",
            workingDir=".",
            commandLine="python -m demo.task1",
            outputFilePath="task1.output.log"
        ),
        TaskInfo(
            name="task 2",
            workingDir=".",
            commandLine="python -m demo.task2",
            outputFilePath="task2.output.log"
        ),
    ]

    print('running task scheduler...')

    scheduler = TaskScheduler('./logs')
    main_task = asyncio.create_task(scheduler.run())

    for t in tasks:
        scheduler.add_task(t)

    await main_task

    print('task scheduler exited.')


if __name__ == "__main__":
    asyncio.run(demo())
