#!/bin/bash

#check mode for options -m 'local_container' and 'local' (which is default if nothing has been given) other options lead to error

while getopts m: option
do
case "${option}"
in
m) MODE=${OPTARG};;
esac
done

if [ -z "$MODE" ]; then
    MODE="local"
fi

if [ "$MODE" = "local_container" ]; then
    echo "Starting services and backend in local container"
    docker-compose -f dc-local-dev-services.yml -f dc-local-dev-container-backend.yml up -d
    echo "Local containers started"
elif [ "$MODE" = "local" ]; then
    echo "Starting local services, you can use "
    npm run start:local
    echo "Local started"
else
    echo "Error: Wrong mode. Please use -m 'local_container' or 'local'"
fi
