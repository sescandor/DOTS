#! /bin/sh

PROTO_FILE=$1

PROTO_FULL_PATH=$PWD/$PROTO_FILE 

protoc -I="$PWD" --python_out="$PWD" "$PROTO_FULL_PATH"
