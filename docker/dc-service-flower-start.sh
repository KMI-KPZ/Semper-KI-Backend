#!/bin/sh
cd /data
echo "Starting Flower with REDIS_HOST=${REDIS_HOST} REDIS_PORT=${REDIS_PORT} REDISPW=${REDISPW}"
exec celery --broker=redis://:${REDISPW}@${REDIS_HOST}:${REDIS_PORT}/0 flower --port=8888
