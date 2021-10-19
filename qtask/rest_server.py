import asyncio
import logging
import os
import threading

from fastapi import FastAPI

import scheduler
from scheduler import Scheduler
from schemas import TaskStatusList, TaskInfo
from store import StoreDB
from utils import setup_logger, setup_data_dirs

# setup data
setup_data_dirs()

# setup logger
setup_logger()
logger = logging.getLogger('server')

# FastAPI app
app = FastAPI()

# task scheduler
task_scheduler = Scheduler(StoreDB())


@app.get("/")
def read_root():
    return {"Hello": "QTask"}


@app.get("/status", response_model=TaskStatusList)
def get_status() -> TaskStatusList:
    return task_scheduler.get_status()


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    return {"item_id": task_id}


@app.post("/tasks")
def add_task(task: TaskInfo):
    task_scheduler.add_task(task)
    return task


def run_scheduler_loop(loop):
    print('scheduler event loop start')
    asyncio.set_event_loop(loop)
    loop.run_forever()
    print('scheduler event loop end')


if os.name == 'nt':
    scheduler_loop = asyncio.ProactorEventLoop()
else:
    scheduler_loop = asyncio.new_event_loop()
scheduler_loop_thread = threading.Thread(target=run_scheduler_loop, args=(scheduler_loop,), daemon=False)
scheduler_loop_thread.start()

asyncio.run_coroutine_threadsafe(scheduler.main(task_scheduler), scheduler_loop)
