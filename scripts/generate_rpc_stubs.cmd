set PROTOS_PATH=%~dp0..\qtask\protos
set OUTPUT_PATH=%~dp0..\qtask\protos
python -m grpc_tools.protoc ^
-I %PROTOS_PATH% ^
--python_betterproto_out=%OUTPUT_PATH% ^
%PROTOS_PATH%/qtaskd.proto
