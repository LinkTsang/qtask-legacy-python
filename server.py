import asyncio
import logging
import os
import threading

from fastapi import FastAPI

import qtaskd
from TaskScheduler import TaskScheduler
from utils import setup_logger

# setup logger
setup_logger()
logger = logging.getLogger('server')

# FastAPI app
app = FastAPI()

# task scheduler
scheduler = TaskScheduler('./logs')


@app.get("/")
def read_root():
    return {"Hello": "QTask"}


@app.get("/status")
def get_status():
    return str(scheduler.get_status())


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    return {"item_id": task_id}


def run_scheduler_loop(loop):
    print('scheduler event loop start')
    asyncio.set_event_loop(loop)
    loop.run_forever()
    print('scheduler event loop end')


if os.name == 'nt':
    scheduler_loop = asyncio.ProactorEventLoop()
else:
    scheduler_loop = asyncio.new_event_loop()
scheduler_loop_thread = threading.Thread(target=run_scheduler_loop, args=(scheduler_loop,), daemon=True)
scheduler_loop_thread.start()

asyncio.run_coroutine_threadsafe(qtaskd.main(scheduler), scheduler_loop)