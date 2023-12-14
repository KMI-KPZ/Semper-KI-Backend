#!/bin/sh
<<<<<<<< HEAD:MSQ/docker/dc-service-redis-start.sh
echo "Starting Redis"
exec docker-entrypoint.sh --save 60 1 --loglevel warning --requirepass $REDISPW
========
exec docker-entrypoint.sh --save 60 1 --loglevel warning --requirepass $REDIS_PASSWORD
>>>>>>>> dev:MSQ/docker/docker-service-redis-start.sh
