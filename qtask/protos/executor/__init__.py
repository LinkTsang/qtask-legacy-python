# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: executor.proto
# plugin: python-betterproto
from dataclasses import dataclass
from datetime import datetime
from typing import AsyncIterator, Dict

import betterproto
import grpclib
from betterproto.grpc.grpclib_server import ServiceBase


class ExecutorStatus(betterproto.Enum):
    IDLE = 0
    BUSY = 1


@dataclass(eq=False, repr=False)
class WatchResponse(betterproto.Message):
    status: "ExecutorStatus" = betterproto.enum_field(1)


@dataclass(eq=False, repr=False)
class RunTaskResponse(betterproto.Message):
    id: str = betterproto.string_field(1)
    status: str = betterproto.string_field(2)
    message: str = betterproto.string_field(3)


@dataclass(eq=False, repr=False)
class Request(betterproto.Message):
    message: str = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class Reply(betterproto.Message):
    message: str = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class TaskDetail(betterproto.Message):
    id: str = betterproto.string_field(1)
    status: str = betterproto.string_field(2)
    created_at: datetime = betterproto.message_field(3)
    started_at: datetime = betterproto.message_field(4)
    paused_at: datetime = betterproto.message_field(5)
    terminated_at: datetime = betterproto.message_field(6)
    name: str = betterproto.string_field(7)
    description: str = betterproto.string_field(8)
    working_dir: str = betterproto.string_field(9)
    command_line: str = betterproto.string_field(10)
    output_file_path: str = betterproto.string_field(11)
    message: str = betterproto.string_field(12)


@dataclass(eq=False, repr=False)
class GetTaskRequest(betterproto.Message):
    pass


@dataclass(eq=False, repr=False)
class GetTaskReply(betterproto.Message):
    task_id: str = betterproto.string_field(1)
    status: str = betterproto.string_field(2)


@dataclass(eq=False, repr=False)
class ExecutorInfo(betterproto.Message):
    host: str = betterproto.string_field(1)
    port: int = betterproto.int32_field(2)


class ExecutorStub(betterproto.ServiceStub):
    async def echo(self, *, message: str = "") -> "Reply":

        request = Request()
        request.message = message

        return await self._unary_unary("/executor.Executor/Echo", request, Reply)

    async def watch(self) -> AsyncIterator["WatchResponse"]:

        request = betterproto_lib_google_protobuf.Empty()

        async for response in self._unary_stream(
                "/executor.Executor/Watch",
                request,
                WatchResponse,
        ):
            yield response

    async def run_task(
            self,
            *,
            id: str = "",
            status: str = "",
            created_at: datetime = None,
            started_at: datetime = None,
            paused_at: datetime = None,
            terminated_at: datetime = None,
            name: str = "",
            description: str = "",
            working_dir: str = "",
            command_line: str = "",
            output_file_path: str = "",
            message: str = "",
    ) -> AsyncIterator["RunTaskResponse"]:

        request = TaskDetail()
        request.id = id
        request.status = status
        if created_at is not None:
            request.created_at = created_at
        if started_at is not None:
            request.started_at = started_at
        if paused_at is not None:
            request.paused_at = paused_at
        if terminated_at is not None:
            request.terminated_at = terminated_at
        request.name = name
        request.description = description
        request.working_dir = working_dir
        request.command_line = command_line
        request.output_file_path = output_file_path
        request.message = message

        async for response in self._unary_stream(
                "/executor.Executor/RunTask",
                request,
                RunTaskResponse,
        ):
            yield response

    async def get_task(self) -> "GetTaskReply":

        request = GetTaskRequest()

        return await self._unary_unary(
            "/executor.Executor/GetTask", request, GetTaskReply
        )


class ExecutorBase(ServiceBase):
    async def echo(self, message: str) -> "Reply":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def watch(self) -> AsyncIterator["WatchResponse"]:
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

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
    ) -> AsyncIterator["RunTaskResponse"]:
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_task(self) -> "GetTaskReply":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def __rpc_echo(self, stream: grpclib.server.Stream) -> None:
        request = await stream.recv_message()

        request_kwargs = {
            "message": request.message,
        }

        response = await self.echo(**request_kwargs)
        await stream.send_message(response)

    async def __rpc_watch(self, stream: grpclib.server.Stream) -> None:
        request = await stream.recv_message()

        request_kwargs = {}

        await self._call_rpc_handler_server_stream(
            self.watch,
            stream,
            request_kwargs,
        )

    async def __rpc_run_task(self, stream: grpclib.server.Stream) -> None:
        request = await stream.recv_message()

        request_kwargs = {
            "id": request.id,
            "status": request.status,
            "created_at": request.created_at,
            "started_at": request.started_at,
            "paused_at": request.paused_at,
            "terminated_at": request.terminated_at,
            "name": request.name,
            "description": request.description,
            "working_dir": request.working_dir,
            "command_line": request.command_line,
            "output_file_path": request.output_file_path,
            "message": request.message,
        }

        await self._call_rpc_handler_server_stream(
            self.run_task,
            stream,
            request_kwargs,
        )

    async def __rpc_get_task(self, stream: grpclib.server.Stream) -> None:
        request = await stream.recv_message()

        request_kwargs = {}

        response = await self.get_task(**request_kwargs)
        await stream.send_message(response)

    def __mapping__(self) -> Dict[str, grpclib.const.Handler]:
        return {
            "/executor.Executor/Echo": grpclib.const.Handler(
                self.__rpc_echo,
                grpclib.const.Cardinality.UNARY_UNARY,
                Request,
                Reply,
            ),
            "/executor.Executor/Watch": grpclib.const.Handler(
                self.__rpc_watch,
                grpclib.const.Cardinality.UNARY_STREAM,
                betterproto_lib_google_protobuf.Empty,
                WatchResponse,
            ),
            "/executor.Executor/RunTask": grpclib.const.Handler(
                self.__rpc_run_task,
                grpclib.const.Cardinality.UNARY_STREAM,
                TaskDetail,
                RunTaskResponse,
            ),
            "/executor.Executor/GetTask": grpclib.const.Handler(
                self.__rpc_get_task,
                grpclib.const.Cardinality.UNARY_UNARY,
                GetTaskRequest,
                GetTaskReply,
            ),
        }


import betterproto.lib.google.protobuf as betterproto_lib_google_protobuf
