# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: qtaskd.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()

from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2

DESCRIPTOR = _descriptor.FileDescriptor(
  name='qtaskd.proto',
  package='qtaskd',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x0cqtaskd.proto\x12\x06qtaskd\x1a\x1fgoogle/protobuf/timestamp.proto\"\x1a\n\x07Request\x12\x0f\n\x07message\x18\x01 \x01(\t\"\x18\n\x05Reply\x12\x0f\n\x07message\x18\x01 \x01(\t\"\x94\x03\n\x0eRunTaskRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0e\n\x06status\x18\x02 \x01(\t\x12.\n\ncreated_at\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x33\n\nstarted_at\x18\x04 \x01(\x0b\x32\x1a.google.protobuf.TimestampH\x00\x88\x01\x01\x12\x32\n\tpaused_at\x18\x05 \x01(\x0b\x32\x1a.google.protobuf.TimestampH\x01\x88\x01\x01\x12\x36\n\rterminated_at\x18\x06 \x01(\x0b\x32\x1a.google.protobuf.TimestampH\x02\x88\x01\x01\x12\x0c\n\x04name\x18\x07 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x08 \x01(\t\x12\x13\n\x0bworking_dir\x18\t \x01(\t\x12\x14\n\x0c\x63ommand_line\x18\n \x01(\t\x12\x18\n\x10output_file_path\x18\x0b \x01(\tB\r\n\x0b_started_atB\x0c\n\n_paused_atB\x10\n\x0e_terminated_at\"\x10\n\x0eGetTaskRequest\"*\n\x0cGetTaskReply\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0e\n\x06status\x18\x02 \x01(\t2\xa6\x01\n\x0bQTaskDaemon\x12(\n\x04\x45\x63ho\x12\x0f.qtaskd.Request\x1a\r.qtaskd.Reply\"\x00\x12\x32\n\x07RunTask\x12\x16.qtaskd.RunTaskRequest\x1a\r.qtaskd.Reply\"\x00\x12\x39\n\x07GetTask\x12\x16.qtaskd.GetTaskRequest\x1a\x14.qtaskd.GetTaskReply\"\x00\x62\x06proto3'
  ,
  dependencies=[google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR, ])

_REQUEST = _descriptor.Descriptor(
  name='Request',
  full_name='qtaskd.Request',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='message', full_name='qtaskd.Request.message', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=57,
  serialized_end=83,
)

_REPLY = _descriptor.Descriptor(
  name='Reply',
  full_name='qtaskd.Reply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='message', full_name='qtaskd.Reply.message', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=85,
  serialized_end=109,
)

_RUNTASKREQUEST = _descriptor.Descriptor(
  name='RunTaskRequest',
  full_name='qtaskd.RunTaskRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='qtaskd.RunTaskRequest.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='status', full_name='qtaskd.RunTaskRequest.status', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='created_at', full_name='qtaskd.RunTaskRequest.created_at', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='started_at', full_name='qtaskd.RunTaskRequest.started_at', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='paused_at', full_name='qtaskd.RunTaskRequest.paused_at', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='terminated_at', full_name='qtaskd.RunTaskRequest.terminated_at', index=5,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='name', full_name='qtaskd.RunTaskRequest.name', index=6,
      number=7, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='description', full_name='qtaskd.RunTaskRequest.description', index=7,
      number=8, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='working_dir', full_name='qtaskd.RunTaskRequest.working_dir', index=8,
      number=9, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='command_line', full_name='qtaskd.RunTaskRequest.command_line', index=9,
      number=10, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='output_file_path', full_name='qtaskd.RunTaskRequest.output_file_path', index=10,
      number=11, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='_started_at', full_name='qtaskd.RunTaskRequest._started_at',
      index=0, containing_type=None,
      create_key=_descriptor._internal_create_key,
      fields=[]),
    _descriptor.OneofDescriptor(
      name='_paused_at', full_name='qtaskd.RunTaskRequest._paused_at',
      index=1, containing_type=None,
      create_key=_descriptor._internal_create_key,
      fields=[]),
    _descriptor.OneofDescriptor(
      name='_terminated_at', full_name='qtaskd.RunTaskRequest._terminated_at',
      index=2, containing_type=None,
      create_key=_descriptor._internal_create_key,
      fields=[]),
  ],
  serialized_start=112,
  serialized_end=516,
)

_GETTASKREQUEST = _descriptor.Descriptor(
  name='GetTaskRequest',
  full_name='qtaskd.GetTaskRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=518,
  serialized_end=534,
)

_GETTASKREPLY = _descriptor.Descriptor(
  name='GetTaskReply',
  full_name='qtaskd.GetTaskReply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='qtaskd.GetTaskReply.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='status', full_name='qtaskd.GetTaskReply.status', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=536,
  serialized_end=578,
)

_RUNTASKREQUEST.fields_by_name['created_at'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_RUNTASKREQUEST.fields_by_name['started_at'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_RUNTASKREQUEST.fields_by_name['paused_at'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_RUNTASKREQUEST.fields_by_name['terminated_at'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_RUNTASKREQUEST.oneofs_by_name['_started_at'].fields.append(
  _RUNTASKREQUEST.fields_by_name['started_at'])
_RUNTASKREQUEST.fields_by_name['started_at'].containing_oneof = _RUNTASKREQUEST.oneofs_by_name['_started_at']
_RUNTASKREQUEST.oneofs_by_name['_paused_at'].fields.append(
  _RUNTASKREQUEST.fields_by_name['paused_at'])
_RUNTASKREQUEST.fields_by_name['paused_at'].containing_oneof = _RUNTASKREQUEST.oneofs_by_name['_paused_at']
_RUNTASKREQUEST.oneofs_by_name['_terminated_at'].fields.append(
  _RUNTASKREQUEST.fields_by_name['terminated_at'])
_RUNTASKREQUEST.fields_by_name['terminated_at'].containing_oneof = _RUNTASKREQUEST.oneofs_by_name['_terminated_at']
DESCRIPTOR.message_types_by_name['Request'] = _REQUEST
DESCRIPTOR.message_types_by_name['Reply'] = _REPLY
DESCRIPTOR.message_types_by_name['RunTaskRequest'] = _RUNTASKREQUEST
DESCRIPTOR.message_types_by_name['GetTaskRequest'] = _GETTASKREQUEST
DESCRIPTOR.message_types_by_name['GetTaskReply'] = _GETTASKREPLY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Request = _reflection.GeneratedProtocolMessageType('Request', (_message.Message,), {
  'DESCRIPTOR': _REQUEST,
  '__module__': 'qtaskd_pb2'
  # @@protoc_insertion_point(class_scope:qtaskd.Request)
})
_sym_db.RegisterMessage(Request)

Reply = _reflection.GeneratedProtocolMessageType('Reply', (_message.Message,), {
  'DESCRIPTOR': _REPLY,
  '__module__': 'qtaskd_pb2'
  # @@protoc_insertion_point(class_scope:qtaskd.Reply)
})
_sym_db.RegisterMessage(Reply)

RunTaskRequest = _reflection.GeneratedProtocolMessageType('RunTaskRequest', (_message.Message,), {
  'DESCRIPTOR': _RUNTASKREQUEST,
  '__module__': 'qtaskd_pb2'
  # @@protoc_insertion_point(class_scope:qtaskd.RunTaskRequest)
})
_sym_db.RegisterMessage(RunTaskRequest)

GetTaskRequest = _reflection.GeneratedProtocolMessageType('GetTaskRequest', (_message.Message,), {
  'DESCRIPTOR': _GETTASKREQUEST,
  '__module__': 'qtaskd_pb2'
  # @@protoc_insertion_point(class_scope:qtaskd.GetTaskRequest)
})
_sym_db.RegisterMessage(GetTaskRequest)

GetTaskReply = _reflection.GeneratedProtocolMessageType('GetTaskReply', (_message.Message,), {
  'DESCRIPTOR': _GETTASKREPLY,
  '__module__': 'qtaskd_pb2'
  # @@protoc_insertion_point(class_scope:qtaskd.GetTaskReply)
})
_sym_db.RegisterMessage(GetTaskReply)

_QTASKDAEMON = _descriptor.ServiceDescriptor(
  name='QTaskDaemon',
  full_name='qtaskd.QTaskDaemon',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=581,
  serialized_end=747,
  methods=[
    _descriptor.MethodDescriptor(
      name='Echo',
      full_name='qtaskd.QTaskDaemon.Echo',
      index=0,
      containing_service=None,
      input_type=_REQUEST,
      output_type=_REPLY,
      serialized_options=None,
      create_key=_descriptor._internal_create_key,
    ),
    _descriptor.MethodDescriptor(
      name='RunTask',
      full_name='qtaskd.QTaskDaemon.RunTask',
      index=1,
      containing_service=None,
      input_type=_RUNTASKREQUEST,
      output_type=_REPLY,
      serialized_options=None,
      create_key=_descriptor._internal_create_key,
    ),
    _descriptor.MethodDescriptor(
      name='GetTask',
      full_name='qtaskd.QTaskDaemon.GetTask',
      index=2,
      containing_service=None,
      input_type=_GETTASKREQUEST,
      output_type=_GETTASKREPLY,
      serialized_options=None,
      create_key=_descriptor._internal_create_key,
    ),
  ])
_sym_db.RegisterServiceDescriptor(_QTASKDAEMON)

DESCRIPTOR.services_by_name['QTaskDaemon'] = _QTASKDAEMON

# @@protoc_insertion_point(module_scope)
