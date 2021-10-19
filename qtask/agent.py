import asyncio
import logging
from typing import Optional, Dict

from betterproto import Casing
from grpclib.client import Channel
from kazoo.client import KazooClient
from kazoo.protocol.states import KazooState, ZnodeStat

from qtask.config import config
from qtask.protos.executor import ExecutorStub, ExecutorInfo, ExecutorInfoStatus
from qtask.schemas import TaskInfo, TaskId
from qtask.utils import Observable, setup_logger

logger = logging.getLogger('qtask.agent')


class TaskAgent:
    def __init__(self):
        self.zk_hosts = config["QTASK_ZOOKEEPER_HOSTS"]

        self.zk_client = KazooClient(hosts=self.zk_hosts)
        self.zk_last_state = KazooState.LOST

        self.cond_executor_node_changed = asyncio.Condition()

        self._task_done = Observable()
        self._task_failed = Observable()
        self._executor_node_updated = Observable()
        self._executor_node_removed = Observable()

        self.executor_nodes: Dict[str, ExecutorInfo] = {}

    @property
    def task_done(self) -> Observable:
        return self._task_done

    @property
    def task_failed(self) -> Observable:
        return self._task_failed

    @property
    def executor_updated(self) -> Observable:
        return self._executor_node_updated

    @property
    def executor_removed(self) -> Observable:
        return self._executor_node_removed

    def is_any_executor_idle(self) -> bool:
        for node in self.executor_nodes.values():
            if node.status == ExecutorInfoStatus.IDLE:
                return True
        return False

    def start(self):
        zk = self.zk_client
        loop = asyncio.get_event_loop()

        @zk.add_listener
        def zk_listener(state: KazooState):
            if state == KazooState.LOST:
                logger.info('zookeeper state changed: %s', state)
            elif state == KazooState.SUSPENDED:
                logger.info('zookeeper state changed: %s', state)
            elif state == KazooState.CONNECTED:
                logger.info('zookeeper state changed: %s', state)
            else:
                logger.error('unknown zookeeper state: %s', state)

            self.zk_last_state = state

        @zk.ChildrenWatch('/qtask/executor')
        def watch_qtaskd_rpc_node(children):
            logger.info('/qtask/executor children update: %r', children)
            for node in children:
                path = f'/qtask/executor/{node}'
                asyncio.run_coroutine_threadsafe(self._handle_executor_node_changed(path), loop)

        zk.start()

    async def _handle_executor_node_changed(self, path: str) -> None:
        zk = self.zk_client
        stat: Optional[ZnodeStat] = zk.exists(path)
        if stat:
            data: bytes
            data, stat = zk.get(path)
            executor_info = ExecutorInfo.FromString(data)

            logger.debug('executor node@%s updated: [%s:%d] status=%s, %s',
                         path,
                         executor_info.host,
                         executor_info.port,
                         executor_info.status,
                         stat)

            self.executor_nodes[path] = executor_info

            message = await self._echo(executor_info)
            logger.debug("qtask agent received from [%s:%d]: %s",
                         executor_info.host,
                         executor_info.port,
                         message)

            self._executor_node_updated.fire(executor_info)
        else:
            address = self.executor_nodes[path]
            logger.debug('executor node@%s removed: %r, %s', path, address, stat)
            del self.executor_nodes[path]

            self._executor_node_removed.fire(address)

        async with self.cond_executor_node_changed:
            self.cond_executor_node_changed.notify_all()

    def _acquire_idle_executor_node(self) -> Optional[ExecutorInfo]:
        for node in self.executor_nodes.values():
            if node.status == ExecutorInfoStatus.IDLE:
                node.status = ExecutorInfoStatus.BUSY
                return node
        return None

    async def _release_executor_node(self, executor_node: ExecutorInfo):
        executor_node.status = ExecutorInfoStatus.IDLE
        async with self.cond_executor_node_changed:
            self.cond_executor_node_changed.notify_all()

    @staticmethod
    async def _echo(executor_info: ExecutorInfo) -> str:
        async with Channel(host=executor_info.host, port=executor_info.port) as channel:
            stub = ExecutorStub(channel)
            response = await stub.echo(message='hi')
        return response.message

    async def schedule_task(self, task: TaskInfo) -> TaskInfo:
        executor_node = self._acquire_idle_executor_node()
        if not executor_node:
            raise RuntimeError('Not available executor nodes!')
        try:
            async with Channel(host=executor_node.host, port=executor_node.port) as channel:
                stub = ExecutorStub(channel)
                response = await stub.run_task(**task.dict())
            return TaskInfo(**response.to_dict(casing=Casing.SNAKE))
        finally:
            await self._release_executor_node(executor_node)

    async def get_task_status(self, task_id: TaskId):
        raise NotImplementedError('Method not implemented!')


def main():
    setup_logger()

    agent = TaskAgent()
    loop = asyncio.get_event_loop()
    agent.start()
    loop.run_forever()
    print('exited.')


if __name__ == '__main__':
    main()
