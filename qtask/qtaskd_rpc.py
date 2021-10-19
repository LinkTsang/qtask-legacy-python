import asyncio
import logging
from datetime import datetime
from typing import Optional

import grpclib
from grpclib.server import Server
from kazoo.client import KazooClient
from kazoo.protocol.states import KazooState

from qtask.config import config
from qtask.protos.qtaskd import QTaskDaemonBase, GetTaskReply, Reply, ExecutorInfo, ExecutorInfoStatus, TaskDetail
from qtask.qtaskd import TaskDaemon
from qtask.schemas import TaskInfo
from qtask.utils import setup_logger

logger = logging.getLogger('qtaskd_rpc')


class QTaskDaemonService(QTaskDaemonBase):

    def __init__(self, server: 'TaskDaemonRpcServer', daemon: TaskDaemon):
        self.server = server
        self.daemon = daemon

    async def echo(self, message: str) -> Reply:
        return Reply(message)

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
    ) -> Reply:
        self.server.executor_info.status = ExecutorInfoStatus.BUSY
        self.server.update_node()

        task_info = await self.daemon.run_task(TaskInfo(
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
        ))

        self.server.executor_info.status = ExecutorInfoStatus.IDLE
        self.server.update_node()

        return TaskDetail.from_dict(**task_info.dict())

    async def get_task(self) -> GetTaskReply:
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)


class TaskDaemonRpcServer:
    def __init__(self, daemon: TaskDaemon):
        daemon.task_done.on(self._handle_task_done)
        self.task_daemon_service = QTaskDaemonService(self, daemon)

        self.grpc_host = config["QTASK_DAEMON_RPC_HOST"]
        self.grpc_port = config["QTASK_DAEMON_RPC_PORT"]
        self.grpc_address = f'{self.grpc_host}:{self.grpc_port}'

        self.zk_hosts = config["QTASK_ZOOKEEPER_HOSTS"]
        self.zk_client = KazooClient(hosts=self.zk_hosts)
        self.zk_last_state = KazooState.LOST
        self._current_zk_node: Optional[str] = None
        self.executor_info = ExecutorInfo(host=self.grpc_host, port=self.grpc_port, status=ExecutorInfoStatus.IDLE)

    async def run(self):
        server = Server([self.task_daemon_service])
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
                logger.error('unknown zookeeper state:', state)

            self.zk_last_state = state

        self.zk_client.start()
        self.register_rpc_node()

        await server.wait_closed()

    def register_rpc_node(self):
        self.zk_client.ensure_path('/qtask/qtaskd')
        self._current_zk_node = self.zk_client.create('/qtask/qtaskd/qtask-instance',
                                                      self.executor_info.SerializeToString(),
                                                      ephemeral=True,
                                                      sequence=True)
        logger.info('register rpc node: %s', self._current_zk_node)

    def update_node(self):
        self.zk_client.set(self._current_zk_node, self.executor_info.SerializeToString())

    def _handle_task_done(self, task: TaskInfo):
        pass


if __name__ == '__main__':
    setup_logger()
    qtaskd = TaskDaemon()
    rpc_service = TaskDaemonRpcServer(qtaskd)
    asyncio.run(rpc_service.run())
