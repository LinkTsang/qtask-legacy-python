import asyncio
import logging
import os
from asyncio.subprocess import Process
from datetime import datetime
from os.path import join as pjoin
from typing import Set

from schemas import TaskInfo, TaskId, TaskStatus
from store import Store

logger = logging.getLogger(__name__)


class TaskScheduler:
    def __init__(self, store: Store, log_dir: str = './logs', max_concurrency_tasks=1):
        self.store = store
        self.log_dir = log_dir
        self.max_concurrency_tasks = max_concurrency_tasks

        self.task_output_dir = pjoin(log_dir, 'tasks')

        self.asyncio_initialized = False

        self._waiting_events: Set[asyncio.Future] = set()

        self._event_task_schedule = None
        self._event_exit = None

        self._asyncio_tasks: Set[asyncio.Future] = set()

        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.task_output_dir, exist_ok=True)

    def init_asyncio(self):
        self._event_task_schedule = asyncio.Event()
        self._event_exit = asyncio.Event()

        self.asyncio_initialized = True

    def add_task(self, task: TaskInfo):
        self.store.enqueue_task(task)
        self._event_task_schedule.set()

    def get_status(self):
        store = self.store
        running_tasks = store.get_activating_tasks()
        pending_tasks = store.get_activating_tasks()
        terminated_tasks = self.store.get_terminated_tasks()

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

        self._check_and_clean_detached_tasks()

        waiting_events = self._waiting_events

        waiting_events.add(asyncio.create_task(self._wait_event_task_schedule()))

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
                    self._event_task_schedule.set()
                    asyncio_tasks.remove(t)

            if self._event_exit.is_set():
                break

        logger.info('exit')

    def exit(self):
        self._event_exit.set()

    async def _wait_event_task_schedule(self):
        store = self.store

        await self._event_task_schedule.wait()
        self._event_task_schedule.clear()

        logger.debug('_event_task_schedule set')

        while store.exists_pending_tasks() \
                and self.max_concurrency_tasks > store.count_activating_tasks():
            task = store.dequeue_task()
            task.started_at = datetime.now()
            task.status = TaskStatus.READY
            store.update_task(task)

            self._asyncio_tasks.add(asyncio.create_task(self._run_task(task.id)))

        self._waiting_events.add(
            asyncio.create_task(self._wait_event_task_schedule()))

    def _check_and_clean_detached_tasks(self):
        store = self.store
        tasks = store.get_activating_tasks()
        if tasks:
            logger.warning('%d tasks detached', len(tasks))
            for t in tasks:
                logger.error('task %r@%s detached from status %r', t.name, t.id, t.status)
                store.update_task_status_by_id(t.id, TaskStatus.DETACHED)

    async def _wait_event_exit(self):
        await self._event_exit.wait()

        logger.debug('_wait_exit_event set')

        waiting_events = self._waiting_events
        waiting_events.add(asyncio.create_task(self._wait_event_exit()))

    async def _run_task(self, task_id: TaskId):
        store = self.store

        task = store.get_task_by_id(task_id)
        status = task.status
        cmd = task.command_line
        output_dir = pjoin(self.task_output_dir, task_id)
        os.makedirs(output_dir, exist_ok=True)
        output_file_path = pjoin(output_dir, task.output_file_path)

        if status != TaskStatus.READY:
            logger.warning('task %r@%s status is not READY', task.name, task_id)

            task.status = TaskStatus.ERROR
            task.terminated_at = datetime.now()
            store.update_task(task)

            self._raise_task_failed(task)

            return

        with open(output_file_path, 'w') as output_file:
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=output_file,
                stderr=output_file)

            _ = await proc.wait()

        task.status = TaskStatus.COMPLETED
        task.terminated_at = datetime.now()
        store.update_task(task)

        self._raise_task_done(task, proc)

    def _raise_task_done(self, task: TaskInfo, proc: Process):
        id_ = task.id
        name = task.name

        logger.info('task %r@%s exited with %d', name, id_, proc.returncode)

    def _raise_task_failed(self, task: TaskInfo):
        id_ = task.id
        name = task.name

        logger.error('task %r@%s failed', name, id_)
