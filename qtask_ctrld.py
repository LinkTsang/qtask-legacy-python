import asyncio
import logging
import os
from datetime import datetime
from typing import Set, List

from config import config
from qtaskd import TaskDaemon
from schemas import TaskInfo, TaskId, TaskStatus, TaskStatusList
from store import Store, StoreDB
from utils import setup_logger, setup_data_dirs

logger = logging.getLogger(__name__)


class TaskControlDaemon:
    def __init__(self, store: Store, log_dir: str = config['QTASK_LOGS_DIR'], max_concurrency_tasks=1):
        self.store = store
        self.log_dir = log_dir
        self.max_concurrency_tasks = max_concurrency_tasks

        self.asyncio_initialized = False

        self._waiting_events: Set[asyncio.Future] = set()

        self._event_task_schedule = None
        self._event_exit = None

        self._asyncio_tasks: Set[asyncio.Future] = set()

        os.makedirs(self.log_dir, exist_ok=True)

        taskd = TaskDaemon()
        taskd.task_done.on(self._handle_task_done)
        taskd.task_failed.on(self._handle_task_failed)

        self._taskd = taskd

    def init_asyncio(self):
        self._event_task_schedule = asyncio.Event()
        self._event_exit = asyncio.Event()

        self.asyncio_initialized = True

    def add_task(self, task: TaskInfo):
        self.store.enqueue_task(task)
        self._event_task_schedule.set()

    def get_status(self) -> TaskStatusList:
        store = self.store
        running_tasks = store.get_activating_tasks()
        pending_tasks = store.get_pending_tasks()
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

            self._asyncio_tasks.add(asyncio.create_task(self._run_task(task)))

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

    async def _run_task(self, task: TaskInfo):
        await self._taskd.run_task(task)

    def _handle_task_done(self, task: TaskInfo):
        self.store.update_task(task)

    def _handle_task_failed(self, task: TaskInfo):
        self.store.update_task(task)


async def main(task_control_daemon: TaskControlDaemon):
    print('running task control daemon...')
    logger.info('running task control daemon...')

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

        task_control_daemon.init_asyncio()
        task = asyncio.create_task(task_control_daemon.run())

        for t in demo_tasks:
            task_control_daemon.add_task(t)

        await task

    except Exception:
        logger.exception('task control daemon uncaught exception')

    logger.info('task control daemon exited.')
    print('task control daemon exited.')


if __name__ == "__main__":
    scheduler = TaskControlDaemon(StoreDB())
    setup_data_dirs()
    setup_logger()
    asyncio.run(main(scheduler))
