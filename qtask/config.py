from typing import cast, TypedDict

from dotenv import dotenv_values


class Config(TypedDict):
    QTASK_APP_NAME: str
    QTASK_DATA_DIR: str
    QTASK_DATABASE_URL: str
    QTASK_DATABASE_TEST_URL: str
    QTASK_LOGS_DIR: str
    QTASK_TASK_LOGS_DIR: str
    QTASK_LOG_FILE_NAME: str
    QTASK_ZOOKEEPER_HOSTS: str
    QTASK_DAEMON_RPC_ADDRESS: str


config: Config = cast(Config, dotenv_values(".env"))
