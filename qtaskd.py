import asyncio
import logging
import os
from datetime import datetime
from os.path import join as pjoin

from config import config
from schemas import TaskInfo, TaskStatus
from utils import Observable

logger = logging.getLogger(__name__)


class TaskDaemon:

    def __init__(self):
        self.log_dir = config["QTASK_LOGS_DIR"]
        self.task_output_dir = config["QTASK_LOGS_DIR"]

        os.makedirs(self.task_output_dir, exist_ok=True)

        self._task_done = Observable()
        self._task_failed = Observable()

    @property
    def task_done(self) -> Observable:
        return self._task_done

    @property
    def task_failed(self) -> Observable:
        return self._task_failed

    async def run_task(self, task: TaskInfo):
        status = task.status
        cmd = task.command_line
        output_dir = pjoin(self.task_output_dir, task.id)
        os.makedirs(output_dir, exist_ok=True)
        output_file_path = pjoin(output_dir, task.output_file_path)

        if status != TaskStatus.READY:
            logger.warning('task %r@%s status is not READY', task.name, task.id)
            logger.error('task %r@%s failed', task.name, task.id)

            task.status = TaskStatus.ERROR
            task.terminated_at = datetime.now()

            self.task_failed.fire(task)

            return

        with open(output_file_path, 'w') as output_file:
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=output_file,
                stderr=output_file)

            _ = await proc.wait()

        logger.info('task %r@%s exited with %d', task.name, task.id, proc.returncode)

        task.status = TaskStatus.COMPLETED
        task.terminated_at = datetime.now()

        self.task_done.fire(task)
