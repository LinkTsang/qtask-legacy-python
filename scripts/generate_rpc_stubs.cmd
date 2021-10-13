set PROTOS_PATH=%~dp0..\protos
set OUTPUT_PATH=%~dp0..
python -m grpc_tools.protoc --experimental_allow_proto3_optional -I %PROTOS_PATH% --python_out=%OUTPUT_PATH% --grpc_python_out=%OUTPUT_PATH% %PROTOS_PATH%/qtaskd.proto