import datetime
from typing import Optional, Literal

from pydantic import BaseModel

TaskStatus = Literal[
    "RUNNING",
    "READY",
    "PENDING",
    "PAUSED",
    "CANCELED",
    "TERMINATED",
    "ERROR",
]


class ProcessInfo(BaseModel):
    current: int
    total: int


class TaskInfo(BaseModel):
    id: str = ""

    status: TaskStatus = "PENDING"
    process: Optional[ProcessInfo]

    createdAt: datetime.datetime = datetime.datetime.now()
    startedAt: Optional[datetime.datetime]
    pausedAt: Optional[datetime.datetime]
    terminatedAt: Optional[datetime.datetime]

    name: str
    description: str = ""

    workingDir: str = ""
    commandLine: str
    outputFilePath: str = "task.log"
