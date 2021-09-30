import abc
from typing import List

import schemas


class Store(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def enqueue_task(self, task: schemas.TaskInfo):
        pass

    @abc.abstractmethod
    def enqueue_tasks(self, tasks: List[schemas.TaskInfo]):
        pass

    @abc.abstractmethod
    def dequeue_task(self) -> schemas.TaskInfo:
        pass

    @abc.abstractmethod
    def update_task(self, task: schemas.TaskInfo):
        pass

    @abc.abstractmethod
    def update_task_status_by_id(self, task_id: str, status: schemas.TaskStatus):
        pass

    @abc.abstractmethod
    def get_tasks(self) -> List[schemas.TaskInfo]:
        pass

    @abc.abstractmethod
    def get_task_by_id(self, id_: str) -> schemas.TaskInfo:
        pass

    @abc.abstractmethod
    def get_activating_tasks(self) -> List[schemas.TaskInfo]:
        pass

    @abc.abstractmethod
    def get_pending_tasks(self) -> List[schemas.TaskInfo]:
        pass

    @abc.abstractmethod
    def get_terminated_tasks(self) -> List[schemas.TaskInfo]:
        pass

    @abc.abstractmethod
    def exists_activating_tasks(self) -> bool:
        pass

    @abc.abstractmethod
    def exists_pending_tasks(self) -> bool:
        pass

    @abc.abstractmethod
    def count_activating_tasks(self) -> int:
        pass

    @abc.abstractmethod
    def count_pending_tasks(self) -> int:
        pass

    @abc.abstractmethod
    def remove_task(self, task_id: str):
        pass
