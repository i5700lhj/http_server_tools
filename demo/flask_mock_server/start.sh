#!/bin/bash

cd $(dirname $0)

nohup python common_mock_server.py &> utility/log/mock_server_front.log &
sleep 0.5

cnt=$(ps -ef|grep "python common_mock_server"|grep -v grep|wc -l)
if [[ $cnt -ne 2 ]]; then
   echo "start common_mock_server failed!!!"
   ps -ef|grep "python common_mock_server"|grep -v grep
   exit 1
else
   echo "start common_mock_server success!"
   exit 0
fi