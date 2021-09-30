from collections import deque
from contextlib import contextmanager
from typing import List, Set, Deque

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, Session

import schemas
from store import Store, models
from store.models import Task, TaskStatus


class StoreDB(Store):
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.engine = create_engine(
            self.db_url, connect_args={"check_same_thread": False}
        )
        models.Base.metadata.create_all(bind=self.engine)
        self.session_local = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        self._running_task_ids: Set[schemas.TaskId] = set()
        self._ready_task_ids: Deque[schemas.TaskId] = deque()
        self._pending_task_ids: Deque[schemas.TaskId] = deque()
        self._terminated_task_ids: List[schemas.TaskId] = []

    @contextmanager
    def get_db(self) -> Session:
        session = self.session_local()
        try:
            yield session
        finally:
            session.close()

    def enqueue_task(self, task: schemas.TaskInfo):
        with self.get_db() as db:
            db.add(Task(**task.dict()))
            db.commit()

    def enqueue_tasks(self, tasks: List[schemas.TaskInfo]):
        with self.get_db() as db:
            db.bulk_save_objects([Task(**t.dict()) for t in tasks])
            db.commit()

    def dequeue_task(self) -> schemas.TaskInfo:
        with self.get_db() as db:
            task = db.query(Task) \
                .filter(Task.status == TaskStatus.PENDING) \
                .order_by(desc(Task.created_at)) \
                .first()
            task.status = TaskStatus.READY
            db.commit()
            return schemas.TaskInfo.from_orm(task)

    def update_task(self, task: schemas.TaskInfo):
        with self.get_db() as db:
            task_db = db.query(Task).filter(Task.id == task.id).first()
            if task_db:
                for k, v in task.dict(exclude_unset=True).items():
                    setattr(task_db, k, v)
            else:
                # insert directly
                db.add(Task(**task.dict()))
            db.commit()

    def update_task_status_by_id(self, task_id: str, status: schemas.TaskStatus):
        with self.get_db() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            task.status = status
            db.commit()

    def get_tasks(self) -> List[schemas.TaskInfo]:
        with self.get_db() as db:
            tasks = db.query(Task).all()
            return list(tasks.map(schemas.TaskInfo.from_orm))

    def get_task_by_id(self, id_: str) -> schemas.TaskInfo:
        with self.get_db() as db:
            task = db.query(Task).filter(Task.id == id_).first()
            return schemas.TaskInfo.from_orm(task)

    def get_activating_tasks(self) -> List[schemas.TaskInfo]:
        with self.get_db() as db:
            tasks = db.query(Task) \
                .filter(Task.status == TaskStatus.READY
                        or Task.status == TaskStatus.RUNNING
                        or Task.status == TaskStatus.PAUSED) \
                .all()
            return list(map(schemas.TaskInfo.from_orm, tasks))

    def get_pending_tasks(self) -> List[schemas.TaskInfo]:
        with self.get_db() as db:
            tasks = db.query(Task) \
                .filter(Task.status == TaskStatus.PENDING) \
                .all()
            return list(map(schemas.TaskInfo.from_orm, tasks))

    def get_terminated_tasks(self) -> List[schemas.TaskInfo]:
        with self.get_db() as db:
            tasks = db.query(Task) \
                .filter(Task.status == TaskStatus.CANCELED
                        or Task.status == TaskStatus.COMPLETED
                        or Task.status == TaskStatus.DETACHED
                        or Task.status == TaskStatus.ERROR) \
                .all()
            return list(tasks.map(schemas.TaskInfo.from_orm))

    def exists_activating_tasks(self) -> bool:
        with self.get_db() as db:
            return db.query(
                db.query(Task).filter(Task.status == TaskStatus.READY
                                      or Task.status == TaskStatus.RUNNING
                                      or Task.status == TaskStatus.PAUSED).exists()
            ).scalar()

    def exists_pending_tasks(self) -> bool:
        with self.get_db() as db:
            return db.query(
                db.query(Task).filter(Task.status == TaskStatus.PENDING).exists()
            ).scalar()

    def count_activating_tasks(self) -> int:
        with self.get_db() as db:
            return db.query(Task).filter(Task.status == TaskStatus.READY
                                         or Task.status == TaskStatus.RUNNING
                                         or Task.status == TaskStatus.PAUSED).count()

    def count_pending_tasks(self) -> int:
        with self.get_db() as db:
            return db.query(Task).filter(Task.status == TaskStatus.PENDING).count()

    def remove_task(self, task_id: str):
        raise NotImplementedError()
