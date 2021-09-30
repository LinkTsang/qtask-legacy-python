import datetime
import enum
import uuid
from typing import Optional, TypeVar

from pydantic import BaseModel, Field
from pydantic.utils import to_camel

TaskId = TypeVar('TaskId', bound=str)


class TaskStatus(enum.Enum):
    READY = "READY"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"

    PENDING = "PENDING"

    CANCELED = "CANCELED"
    COMPLETED = "COMPLETED"
    DETACHED = "DETACHED"
    ERROR = "ERROR"


class TaskInfo(BaseModel):
    id: TaskId = Field(default_factory=lambda: str(uuid.uuid4()))

    status: TaskStatus = TaskStatus.PENDING

    created_at: datetime.datetime = datetime.datetime.now()
    started_at: Optional[datetime.datetime]
    paused_at: Optional[datetime.datetime]
    terminated_at: Optional[datetime.datetime]

    name: str
    description: str = ""

    working_dir: str = ""
    command_line: str
    output_file_path: str = "task.log"

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class ActivatingTaskInfo(TaskInfo):
    process_current: Optional[int]
    process_total: Optional[int]
