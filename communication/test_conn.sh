#!/bin/bash

while true
do
    echo $(sudo lsof -i -P -n | grep LISTEN | grep 5000)
    sleep 1
done
