from typing import List
from TaskScheduler import TaskInfo, TaskScheduler
import asyncio


async def demo():
    tasks: List[TaskInfo] = [
        {
            "name": "task 1",
            "workingDir": ".",
            "commandLine": "python -m demo.task1",
            "outputFilePath": "task1.output.log"
        },
        {
            "name": "task 2",
            "workingDir": ".",
            "commandLine": "python -m demo.task2",
            "outputFilePath": "task2.output.log"
        },
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
