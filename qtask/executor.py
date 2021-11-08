import asyncio
import logging
import os
from datetime import datetime
from os.path import join as pjoin
from typing import Dict

from qtask.config import config
from qtask.schemas import TaskInfo, TaskStatus
from qtask.schemas.Task import TaskId
from qtask.schemas.executor import ExecutorStatus
from qtask.utils import Observable

logger = logging.getLogger(__name__)


class Executor:

    def __init__(self):
        self.log_dir = config["QTASK_LOGS_DIR"]
        self.task_output_dir = config["QTASK_LOGS_DIR"]

        os.makedirs(self.task_output_dir, exist_ok=True)

        self._status: ExecutorStatus = ExecutorStatus.IDLE

        self._tasks: Dict[TaskId, TaskInfo] = {}

        self._status_changed = Observable[TaskInfo]()

    @property
    def task_status_changed(self) -> Observable[TaskInfo]:
        return self._status_changed

    @property
    def status(self) -> ExecutorStatus:
        return self._status

    async def run_task(self, task: TaskInfo) -> TaskInfo:
        status = task.status
        cmd = task.command_line
        output_dir = pjoin(self.task_output_dir, task.id)
        os.makedirs(output_dir, exist_ok=True)
        output_file_path = pjoin(output_dir, task.output_file_path)

        if status != TaskStatus.READY:
            logger.warning('task %r@%s status is not READY', task.name, task.id)
            logger.error('task %r@%s failed', task.name, task.id)

            task.status = TaskStatus.ERROR
            task.message = 'task status is not READY'
            task.terminated_at = datetime.now()

            self._status_changed.fire(task)

            return task

        self._status = ExecutorStatus.BUSY

        with open(output_file_path, 'w') as output_file:
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=output_file,
                stderr=output_file)

            _ = await proc.wait()

        logger.info('task %r@%s exited with %d', task.name, task.id, proc.returncode)

        self._status = ExecutorStatus.IDLE

        task.status = TaskStatus.COMPLETED
        task.terminated_at = datetime.now()

        self._status_changed.fire(task)

        return task
