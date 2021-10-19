from typing import TypedDict

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
    QTASK_EXECUTOR_RPC_HOST: str
    QTASK_EXECUTOR_RPC_PORT: int


def load_config() -> Config:
    annotations = Config.__annotations__
    config = {}
    for k, v in dotenv_values(".env").items():
        t = annotations[k]
        config[k] = t(v)
    return config


config: Config = load_config()
