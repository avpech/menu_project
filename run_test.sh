#!/bin/sh

docker-compose -f docker-compose.test.yaml up --build --no-log-prefix --abort-on-container-exit
