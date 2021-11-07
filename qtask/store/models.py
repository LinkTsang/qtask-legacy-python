from sqlalchemy import Column, String, DateTime, Enum

from .db import Base
from .. import schemas

TaskId = schemas.TaskId

TaskStatus = schemas.TaskStatus


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)

    status = Column(Enum(TaskStatus), nullable=False)

    created_at = Column(DateTime, nullable=False)
    started_at = Column(DateTime, nullable=True)
    paused_at = Column(DateTime, nullable=True)
    terminated_at = Column(DateTime, nullable=True)

    name = Column(String, nullable=False)
    description = Column(String, nullable=False)

    working_dir = Column(String, nullable=False)
    command_line = Column(String, nullable=False)
    output_file_path = Column(String, nullable=False)
    message = Column(String, nullable=False)
