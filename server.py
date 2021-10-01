import asyncio
import logging
import os
import threading

from fastapi import FastAPI

import qtaskd
from TaskScheduler import TaskScheduler
from config import QTASK_DATABASE_URL
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
scheduler = TaskScheduler(StoreDB(QTASK_DATABASE_URL), './logs')


@app.get("/")
def read_root():
    return {"Hello": "QTask"}


@app.get("/status")
def get_status():
    return scheduler.get_status()


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
scheduler_loop_thread = threading.Thread(target=run_scheduler_loop, args=(scheduler_loop,), daemon=False)
scheduler_loop_thread.start()

asyncio.run_coroutine_threadsafe(qtaskd.main(scheduler), scheduler_loop)
