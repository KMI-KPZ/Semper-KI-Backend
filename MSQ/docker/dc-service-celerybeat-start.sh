#!/bin/sh
echo "Starting Celery beat"
exec celery -A module beat --l info
