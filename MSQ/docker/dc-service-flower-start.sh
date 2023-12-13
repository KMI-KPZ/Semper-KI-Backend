#!/bin/sh
cd /data
echo "Starting Flower with REDIS_HOST=${REDIS_HOST} REDIS_PORT=${REDIS_PORT} REDISPW=${REDISPW}"
exec celery --broker=redis://redis:6379/0 flower --port=8888
exec docker network connect semperki-local-dev_semper-ki-dev-network flower

