#!/bin/sh
echo "Starting Redis"
exec docker-entrypoint.sh --save 60 1 --loglevel warning --requirepass $REDISPW