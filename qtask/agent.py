import asyncio
import logging
from typing import Optional, Dict

from betterproto import Casing
from grpclib.client import Channel
from kazoo.client import KazooClient
from kazoo.protocol.states import KazooState, ZnodeStat, WatchedEvent, EventType

from qtask.config import config
from qtask.protos.executor import ExecutorStub, ExecutorInfo, ExecutorInfoStatus
from qtask.schemas import TaskInfo, TaskId
from qtask.utils import Observable, setup_logger

logger = logging.getLogger('qtask.agent')


class ExecutorNode:

    def __init__(self, info: ExecutorInfo, zk_node_path: str, channel: Channel = None):
        self.host: str = info.host
        self.port: int = info.port
        self.status: ExecutorInfoStatus = info.status

        self.zk_node_path: str = zk_node_path

        if not channel:
            channel = Channel(host=self.host, port=self.port)
        self.channel: Channel = channel
        self.stub: ExecutorStub = ExecutorStub(channel)

    async def echo(self, message: str) -> str:
        response = await self.stub.echo(message=message)
        return response.message

    async def schedule_task(self, task: TaskInfo) -> TaskInfo:
        response = await self.stub.run_task(**task.dict())
        return TaskInfo(**response.to_dict(casing=Casing.SNAKE))

    def update_info(self, info: ExecutorInfo):
        if self.host != info.host or self.port != info.port:
            if self.channel:
                self.channel.close()
            self.channel = Channel(host=self.host, port=self.port)
            self.stub = ExecutorStub(self.channel)

            self.host = info.host
            self.port = info.port

        self.status: ExecutorInfoStatus = info.status

    def info(self):
        return ExecutorInfo(self.host, self.port, self.status)

    def close(self):
        self.channel.close()


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

        self.executor_nodes: Dict[str, ExecutorNode] = {}

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
            # NOTE: running in zookeeper worker thread
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
            # NOTE: running in zookeeper worker thread
            logger.info('/qtask/executor children update: %r', children)
            for node in children:
                path = f'/qtask/executor/{node}'
                if path not in self.executor_nodes:
                    asyncio.run_coroutine_threadsafe(self._handle_executor_node_create(path), loop)

        zk.start()

    async def _handle_executor_node_create(self, path: str) -> None:
        zk = self.zk_client
        loop = asyncio.get_event_loop()

        await self._create_executor_node(path)

        @zk.DataWatch(path)
        def node_watcher(data: bytes, stat: ZnodeStat, event: WatchedEvent):
            # NOTE: running in zookeeper worker thread
            logger.debug('executor node changed: path=%r, event=%r, stat=%r', path, event, stat)
            if event:
                if event.type == EventType.CHANGED:
                    info = ExecutorInfo.FromString(data)
                    asyncio.run_coroutine_threadsafe(self._update_executor_node(path, info), loop)
                elif event.type == EventType.DELETED:
                    asyncio.run_coroutine_threadsafe(self._remove_executor_node(path), loop)

    async def _notify_executor_node_changed(self):
        async with self.cond_executor_node_changed:
            self.cond_executor_node_changed.notify_all()

    async def _create_executor_node(self, path: str):
        data: bytes
        data, stat = self.zk_client.get(path)
        info = ExecutorInfo.FromString(data)
        logger.debug('executor node created: path=%r[%s:%d] status=%r, %r',
                     path,
                     info.host,
                     info.port,
                     info.status,
                     stat)
        executor_node = ExecutorNode(info, path)
        self.executor_nodes[path] = executor_node

        message = await executor_node.echo('hi')
        logger.debug("qtask agent received from [%s:%d]: %s",
                     info.host,
                     info.port,
                     message)

        await self._notify_executor_node_changed()

    async def _update_executor_node(self, path: str, info: ExecutorInfo):
        logger.debug('executor node updated: path=%r[%s:%d] status=%r',
                     path,
                     info.host,
                     info.port,
                     info.status
                     )
        executor_node = self.executor_nodes[path]
        executor_node.update_info(info)

        await self._notify_executor_node_changed()

        self._executor_node_updated.fire(info)

    async def _remove_executor_node(self, path: str):
        logger.debug('executor node removed: path=%r, %r',
                     path,
                     self.executor_nodes[path]
                     )
        node = self.executor_nodes[path]
        if node and node.channel:
            node.channel.close()
        self._executor_node_removed.fire(node)
        if node:
            del self.executor_nodes[path]

    def _acquire_idle_executor_node(self) -> Optional[ExecutorNode]:
        for node in self.executor_nodes.values():
            if node.status == ExecutorInfoStatus.IDLE:
                return node
        return None

    async def _release_executor_node(self, executor_node: ExecutorNode) -> None:
        executor_node.status = ExecutorInfoStatus.IDLE
        async with self.cond_executor_node_changed:
            self.cond_executor_node_changed.notify_all()

    async def schedule_task(self, task: TaskInfo) -> TaskInfo:
        executor_node = self._acquire_idle_executor_node()
        if not executor_node:
            raise RuntimeError('Not available executor nodes!')
        try:
            return await executor_node.schedule_task(task)
        finally:
            await self._notify_executor_node_changed()

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
