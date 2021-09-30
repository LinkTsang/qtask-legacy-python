import asyncio
import logging
import os
from asyncio.subprocess import Process
from collections import deque
from datetime import datetime
from os.path import join as pjoin
from typing import Set, Dict, Deque, List

from model import TaskInfo, TaskId

logger = logging.getLogger(__name__)


class TaskScheduler:
    def __init__(self, log_dir: str = './logs'):
        self.log_dir = log_dir
        self.task_output_dir = pjoin(log_dir, 'tasks')

        self.asyncio_initialized = False

        self._waiting_events: Set[asyncio.Future] = set()

        self._event_add_pending_task = None
        self._event_task_ready = None
        self._event_exit = None

        self.tasks: Dict[TaskId, TaskInfo] = {}

        self._asyncio_tasks: Set[asyncio.Future] = set()

        self._running_task_ids: Set[TaskId] = set()
        self._ready_task_ids: Deque[TaskId] = deque()
        self._pending_task_ids: Deque[TaskId] = deque()
        self._terminated_task_ids: List[TaskId] = []

        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.task_output_dir, exist_ok=True)

    def init_asyncio(self):
        self._event_add_pending_task = asyncio.Event()
        self._event_task_ready = asyncio.Event()
        self._event_exit = asyncio.Event()

        self.asyncio_initialized = True

    def add_task(self, task: TaskInfo):
        self.tasks[task.id] = task
        self._pending_task_ids.append(task.id)
        self._event_add_pending_task.set()

    def get_status(self):
        tasks = self.tasks
        running_tasks = [tasks[i] for i in self._running_task_ids]
        pending_tasks = [tasks[i] for i in self._pending_task_ids]
        terminated_tasks = [tasks[i] for i in self._terminated_task_ids]

        return {
            'running_tasks': running_tasks,
            'pending_tasks': pending_tasks,
            'terminated_tasks': terminated_tasks,
        }

    def remove_task(self, task_id: TaskId):
        raise NotImplementedError

    def try_pause_task(self, task_id: TaskId):
        raise NotImplementedError

    def try_resume_task(self, task_id: TaskId):
        raise NotImplementedError

    def try_cancel_task(self, task_id: TaskId):
        raise NotImplementedError

    def kill_task(self, task_id: TaskId):
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
            asyncio_tasks = self._asyncio_tasks
            futures = waiting_events | asyncio_tasks

            if asyncio_tasks:
                logger.debug('running tasks %s', asyncio_tasks)
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

                if t in asyncio_tasks:
                    if t.exception():
                        logger.info(t.exception())
                    asyncio_tasks.remove(t)

            if self._event_exit.is_set():
                break

        logger.info('exit')

    def exit(self):
        self._event_exit.set()

    async def _wait_event_task_add(self):
        await self._event_add_pending_task.wait()
        self._event_add_pending_task.clear()

        logger.debug('_wait_event_add_task set')

        while self._pending_task_ids:
            task = self._pending_task_ids.popleft()
            self._ready_task_ids.append(task)

        if self._ready_task_ids:
            self._event_task_ready.set()

        self._waiting_events.add(
            asyncio.create_task(self._wait_event_task_add()))

    async def _wait_event_task_ready(self):
        await self._event_task_ready.wait()
        self._event_task_ready.clear()

        logger.debug('_event_task_ready set')

        while self._ready_task_ids:
            ready_task_id = self._ready_task_ids.popleft()
            self._asyncio_tasks.add(asyncio.create_task(self._run_task(ready_task_id)))

        self._waiting_events.add(
            asyncio.create_task(self._wait_event_task_ready()))

    async def _wait_event_exit(self):
        await self._event_exit.wait()

        logger.debug('_wait_exit_event set')

        waiting_events = self._waiting_events
        waiting_events.add(asyncio.create_task(self._wait_event_exit()))

    async def _run_task(self, task_id: TaskId):
        task = self.tasks[task_id]
        cmd = task.command_line
        output_dir = pjoin(self.task_output_dir, task_id)
        os.makedirs(output_dir, exist_ok=True)
        output_file_path = pjoin(output_dir, task.output_file_path)

        task.started_at = datetime.now()
        self._running_task_ids.add(task_id)

        with open(output_file_path, 'w') as output_file:
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=output_file,
                stderr=output_file)

            _ = await proc.wait()

        self._running_task_ids.remove(task_id)
        task.terminated_at = datetime.now()
        self._terminated_task_ids.append(task_id)

        self._raise_task_done(task, proc)

    def _raise_task_done(self, task: TaskInfo, proc: Process):
        id_ = task.id
        name = task.name

        logger.info('task %r@%s exited with %d', name, id_, proc.returncode)
