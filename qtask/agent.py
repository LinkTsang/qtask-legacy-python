import asyncio
import logging
from typing import Optional, Dict, Set, AsyncIterator

from betterproto import Enum
from grpclib.client import Channel
from kazoo.client import KazooClient
from kazoo.protocol.states import KazooState, ZnodeStat, WatchedEvent, EventType

from qtask.config import config
from qtask.protos.executor import ExecutorStub, ExecutorInfo, ExecutorStatus
from qtask.schemas import TaskInfo, TaskId
from qtask.utils import setup_logger

logger = logging.getLogger('qtask.agent')


class ExecutorNodeStatus(Enum):
    UNKNOWN = -1
    IDLE = 0
    BUSY = 1
    TERMINATED = 2


class ExecutorNode:

    def __init__(self, info: ExecutorInfo, zk_node_path: str):
        self.status: ExecutorNodeStatus = ExecutorNodeStatus.UNKNOWN
        self.host: str = info.host
        self.port: int = info.port

        self.zk_node_path: str = zk_node_path

        self.channel: Channel = Channel(host=self.host, port=self.port)
        self.stub: ExecutorStub = ExecutorStub(self.channel)

    async def echo(self, message: str) -> str:
        response = await self.stub.echo(message=message)
        return response.message

    async def watch(self) -> AsyncIterator[ExecutorNodeStatus]:
        try:
            async for response in self.stub.watch():
                if response.status == ExecutorStatus.IDLE:
                    self.status = ExecutorNodeStatus.IDLE
                elif response.status == ExecutorStatus.BUSY:
                    self.status = ExecutorNodeStatus.BUSY
                logger.debug(f'status={self.status.name}')
                yield self.status
        except Exception:
            logger.exception('executor node exception: path=[%s:%d] status=%r',
                             self.host,
                             self.port,
                             self.status
                             )
        self.status = ExecutorNodeStatus.TERMINATED
        yield self.status

    async def schedule_task(self, task: TaskInfo) -> AsyncIterator[TaskInfo]:
        async for response in self.stub.run_task(**task.dict()):
            assert task.id == response.id
            task.status = response.status
            task.message = response.message
            yield task

    def update_info(self, info: ExecutorInfo):
        if self.host != info.host or self.port != info.port:
            if self.channel:
                self.channel.close()
            self.channel = Channel(host=self.host, port=self.port)
            self.stub = ExecutorStub(self.channel)

            self.host = info.host
            self.port = info.port

    def info(self) -> ExecutorInfo:
        return ExecutorInfo(self.host, self.port)

    def close(self):
        self.channel.close()


class TaskAgent:
    def __init__(self):
        self.zk_hosts = config["QTASK_ZOOKEEPER_HOSTS"]

        self.zk_client = KazooClient(hosts=self.zk_hosts)
        self.zk_last_state = KazooState.LOST

        self.cond_executor_node_changed = asyncio.Condition()

        self.executor_nodes: Dict[str, ExecutorNode] = {}

        self._executor_node_watching_tasks: Set[asyncio.Task] = set()

    def is_any_executor_idle(self) -> bool:
        for node in self.executor_nodes.values():
            if node.status == ExecutorStatus.IDLE:
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
                    asyncio.run_coroutine_threadsafe(self._handle_executor_node_created(path), loop)

        zk.start()

    async def _handle_executor_node_created(self, path: str) -> None:
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
                    asyncio.run_coroutine_threadsafe(self._handle_executor_node_updated(path, info), loop)
                elif event.type == EventType.DELETED:
                    asyncio.run_coroutine_threadsafe(self._handle_executor_node_removed(path), loop)

    async def _notify_executor_node_changed(self) -> None:
        async with self.cond_executor_node_changed:
            self.cond_executor_node_changed.notify_all()

    async def _create_executor_node(self, path: str):
        data: bytes
        data, stat = self.zk_client.get(path)
        info = ExecutorInfo.FromString(data)
        logger.debug('executor node created: path=%r[%s:%d] %r',
                     path,
                     info.host,
                     info.port,
                     stat)
        executor_node = ExecutorNode(info, path)
        self.executor_nodes[path] = executor_node

        task = asyncio.create_task(self._watch_executor_node(executor_node))
        self._executor_node_watching_tasks.add(task)
        task.add_done_callback(self._executor_node_watching_tasks.remove)

    async def _watch_executor_node(self, node: ExecutorNode) -> None:
        async for status in node.watch():
            logger.debug('executor node updated: path=[%s:%d] status=%r',
                         node.host,
                         node.port,
                         status.name)
            await self._notify_executor_node_changed()

    async def _handle_executor_node_updated(self, path: str, info: ExecutorInfo):
        logger.debug('executor node updated: path=%r[%s:%d]',
                     path,
                     info.host,
                     info.port
                     )
        executor_node = self.executor_nodes[path]
        executor_node.update_info(info)

    async def _handle_executor_node_removed(self, path: str):
        logger.debug('executor node removed: path=%r, %r',
                     path,
                     self.executor_nodes[path]
                     )
        node = self.executor_nodes[path]
        node.close()
        del self.executor_nodes[path]

    def _acquire_idle_executor_node(self) -> Optional[ExecutorNode]:
        for node in self.executor_nodes.values():
            if node.status == ExecutorStatus.IDLE:
                return node
        return None

    async def schedule_task(self, task: TaskInfo) -> AsyncIterator[TaskInfo]:
        executor_node = self._acquire_idle_executor_node()
        if not executor_node:
            raise RuntimeError('Not available executor nodes!')
        async for task in executor_node.schedule_task(task):
            yield task

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
