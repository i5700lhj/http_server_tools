#!/bin/bash

ps -ef|grep -v grep |grep "python common_mock_server"|awk '{print $2}'|xargs kill -9 &>/dev/null
sleep 0.3
if ps -ef|grep -v grep |grep "python common_mock_server"; then
    echo "stop common_mock_server failed!!"
    exit 1
else
    echo "stop common_mock_server success!"
    exit 0
fi