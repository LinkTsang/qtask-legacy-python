import argparse
import asyncio
import logging
from datetime import datetime
from typing import Optional, AsyncIterator

import grpclib
from grpclib.server import Server
from kazoo.client import KazooClient
from kazoo.protocol.states import KazooState

from qtask.config import config
from qtask.executor import Executor
from qtask.protos.executor import (
    ExecutorBase,
    GetTaskReply,
    Reply,
    ExecutorInfo,
    WatchResponse,
    ExecutorStatus,
    RunTaskResponse
)
from qtask.schemas import TaskInfo
from qtask.utils import setup_logger

logger = logging.getLogger('qtaskd_rpc')


class ExecutorService(ExecutorBase):

    def __init__(self):
        self.executor: Executor = Executor()

        self.status: ExecutorStatus = ExecutorStatus.IDLE
        self.status_condition = asyncio.Condition()

    async def echo(self, message: str) -> Reply:
        return Reply(message)

    async def watch(self) -> AsyncIterator[WatchResponse]:
        try:
            while True:
                logger.debug('status=%s', self.status.name)
                yield WatchResponse(status=self.status)
                async with self.status_condition:
                    await self.status_condition.wait()
        except Exception:
            logger.exception('exception in `watch`')
            raise

    async def _update_status(self, status: ExecutorStatus) -> None:
        async with self.status_condition:
            self.status = status
            self.status_condition.notify_all()

    async def run_task(
            self,
            id: str,
            status: str,
            created_at: datetime,
            started_at: datetime,
            paused_at: datetime,
            terminated_at: datetime,
            name: str,
            description: str,
            working_dir: str,
            command_line: str,
            output_file_path: str,
            message: str,
    ) -> AsyncIterator[RunTaskResponse]:
        await self._update_status(ExecutorStatus.BUSY)

        task_info = TaskInfo(
            id=id,
            status=status,
            created_at=created_at,
            started_at=started_at,
            paused_at=paused_at,
            terminated_at=terminated_at,
            name=name,
            description=description,
            working_dir=working_dir,
            command_line=command_line,
            output_file_path=output_file_path,
        )

        # TODO: watch more task status
        task_info = await self.executor.run_task(task_info)

        yield RunTaskResponse(id=id, status=task_info.status, message=task_info.message)

        await self._update_status(ExecutorStatus.IDLE)

    async def get_task(self) -> GetTaskReply:
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)


class ExecutorRpcServer:
    def __init__(self, grpc_host: str, grpc_port: int):
        self.executor_service = ExecutorService()

        self.grpc_host = grpc_host if grpc_host else config["QTASK_EXECUTOR_RPC_HOST"]
        self.grpc_port = grpc_port if grpc_port else config["QTASK_EXECUTOR_RPC_PORT"]
        self.grpc_address = f'{self.grpc_host}:{self.grpc_port}'

        self.zk_hosts = config["QTASK_ZOOKEEPER_HOSTS"]
        self.zk_client = KazooClient(hosts=self.zk_hosts)
        self.zk_last_state = KazooState.LOST
        self._current_zk_node: Optional[str] = None
        self.executor_info = ExecutorInfo(host=self.grpc_host, port=self.grpc_port)

    async def run(self):
        server = Server([self.executor_service])
        await server.start(host=self.grpc_host, port=self.grpc_port)

        zk = self.zk_client

        @zk.add_listener
        def listener(state: KazooState):
            if state == KazooState.LOST:
                print('zookeeper state:', state)
            elif state == KazooState.SUSPENDED:
                print('zookeeper state:', state)
            elif state == KazooState.CONNECTED:
                print('zookeeper state:', state)
            else:
                logger.error('unknown zookeeper state: %s', state)

            self.zk_last_state = state

        self.zk_client.start()
        self.register_rpc_node()

        await server.wait_closed()

    def register_rpc_node(self):
        self.zk_client.ensure_path('/qtask/executor')
        self._current_zk_node = self.zk_client.create('/qtask/executor/qtask-instance',
                                                      self.executor_info.SerializeToString(),
                                                      ephemeral=True,
                                                      sequence=True)
        logger.info('register rpc node: %s', self._current_zk_node)


async def main():
    parser = argparse.ArgumentParser(description='Executor PRC Service.')
    parser.add_argument('--host', type=str, default=config["QTASK_EXECUTOR_RPC_HOST"])
    parser.add_argument('--port', type=int, default=config["QTASK_EXECUTOR_RPC_PORT"])
    args = parser.parse_args()

    setup_logger()
    rpc_service = ExecutorRpcServer(
        args.host,
        args.port
    )
    await rpc_service.run()


if __name__ == '__main__':
    asyncio.run(main())
