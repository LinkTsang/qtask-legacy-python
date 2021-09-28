import asyncio
import logging
import os
import uuid
from asyncio.subprocess import Process
from os.path import join as pjoin
from typing import Set

from model import TaskInfo

logger = logging.getLogger(__name__)


class TaskScheduler:
    def __init__(self, log_dir: str = './logs'):
        self.log_dir = log_dir

        self.asyncio_initialized = False

        self._waiting_events = set()

        self._event_add_pending_task = None
        self._event_task_ready = None
        self._event_exit = None

        self._running_tasks: Set[asyncio.Task] = set()
        self._ready_task_list = []
        self._pending_task_list = []
        self._terminated_task_list = []

        os.makedirs(self.log_dir, exist_ok=True)

    def init_asyncio(self):
        self._event_add_pending_task = asyncio.Event()
        self._event_task_ready = asyncio.Event()
        self._event_exit = asyncio.Event()

        self.asyncio_initialized = True

    def add_task(self, task: TaskInfo):
        task.id = str(uuid.uuid4())
        self._pending_task_list.append(task)
        self._event_add_pending_task.set()

    def get_status(self):
        asyncio_tasks = [{
            'name': t.get_name(),
            'done': t.done(),
        } for t in self._running_tasks]

        return {
            'asyncio_tasks': asyncio_tasks
        }

    def remove_task(self, task_id: str):
        raise NotImplementedError

    def try_pause_task(self, task_id: str):
        raise NotImplementedError

    def try_resume_task(self, task_id: str):
        raise NotImplementedError

    def try_cancel_task(self, task_id: str):
        raise NotImplementedError

    def kill_task(self, task_id: str):
        raise NotImplementedError

    async def run(self):
        if not self.asyncio_initialized:
            logging.error('asyncio is not initialize')
            raise RuntimeError('asyncio is not initialize')

        logger.info('start')

        waiting_events = self._waiting_events

        waiting_events.add(asyncio.create_task(self._wait_event_task_add()))
        waiting_events.add(asyncio.create_task(self._wait_event_task_ready()))

        waiting_events.add(asyncio.create_task(self._wait_event_exit()))

        while True:
            running_tasks = self._running_tasks
            futures = waiting_events | running_tasks

            if running_tasks:
                logger.debug('running tasks %s', running_tasks)
            else:
                logger.debug('no running tasks')

            if len(futures) == 0:
                logger.debug('no futures, exit looping')
                break

            done, pending = await asyncio.wait(
                futures,
                return_when=asyncio.FIRST_COMPLETED)

            logger.debug('asyncio done set %s', done)
            logger.debug('asyncio pending set %s', pending)

            for t in done:
                if t in waiting_events:
                    waiting_events.remove(t)

                if t in running_tasks:
                    if t.exception():
                        logger.info(t.exception())
                    running_tasks.remove(t)

            if self._event_exit.is_set():
                break

        logger.info('exit')

    def exit(self):
        self._event_exit.set()

    async def _wait_event_task_add(self):
        await self._event_add_pending_task.wait()
        self._event_add_pending_task.clear()

        logger.debug('_wait_event_add_task set')

        while self._pending_task_list:
            task = self._pending_task_list.pop()
            self._ready_task_list.append(task)

        if self._ready_task_list:
            self._event_task_ready.set()

        self._waiting_events.add(
            asyncio.create_task(self._wait_event_task_add()))

    async def _wait_event_task_ready(self):
        await self._event_task_ready.wait()
        self._event_task_ready.clear()

        logger.debug('_event_task_ready set')

        while self._ready_task_list:
            ready_task = self._ready_task_list.pop()
            self._running_tasks.add(asyncio.create_task(self._run_task(ready_task)))

        self._waiting_events.add(
            asyncio.create_task(self._wait_event_task_ready()))

    async def _wait_event_exit(self):
        await self._event_exit.wait()

        logger.debug('_wait_exit_event set')

        waiting_events = self._waiting_events
        waiting_events.add(asyncio.create_task(self._wait_event_exit()))

    async def _run_task(self, task: TaskInfo):
        cmd = task.commandLine
        output_dir = pjoin(self.log_dir, task.id)
        os.makedirs(output_dir, exist_ok=True)
        output_file_path = pjoin(output_dir, task.outputFilePath)

        with open(output_file_path, 'w') as output_file:
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=output_file,
                stderr=output_file)

            _ = await proc.wait()

        self._raise_task_done(task, proc)

    def _raise_task_done(self, task: TaskInfo, proc: Process):
        id_ = task.id
        name = task.name

        logger.info('task %r@%s exited with %d', name, id_, proc.returncode)
