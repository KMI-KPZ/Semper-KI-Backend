#!/bin/bash
pwd
echo "Starting SemperKI-Backend"
ENV="production"
MIGRATIONS=1
CHECKS=1
DEBUG=0

while getopts "e:mcd" opt; do
  case $opt in
    e)
      ENV="$OPTARG"
      ;;
    m)
      MIGRATIONS=1
      ;;
    c)
      CHECKS=1
      ;;
    d)
      DEBUG=1
      ;;
    \?)
      echo "Ungültige Option: -$OPTARG" >&2
      exit 1
      ;;
  esac
done

echo "ENVIRONMENT: $ENV"
echo "MIGRATIONS: $MIGRATIONS"
echo "CHECKS: $CHECKS"
echo "DEBUG: $DEBUG"

echo "...Waiting for postgres..."
SLEEP 10

if [ $CHECKS -eq 1 ]; then
  echo "running python manage.py check backend_django --env $ENV"
  python manage.py check backend_django --env "$ENV"
  if [ $? -ne 0 ]; then
    #perhaps db does not exist?
    echo "DJANGO CHECK FAILED - TRYING TO CREATE DB"
    python manage.py create_db --env "$ENV"
    if [ $? -ne 0 ]; then
      echo "DJANGO CHECK FAILED AS WELL AS DB CREATION - ABORTING"
      exit 2
    fi

    echo "running again python manage.py check backend_django --env $ENV"
    python manage.py check backend_django --env "$ENV"
    if [ $? -ne 0 ]; then
      echo "DJANGO CHECK FAILED AGAIN - ABORTING"
      exit 3
    fi
  fi
fi

if [ $MIGRATIONS -eq 1 ]; then
  echo -e "\nrunning python manage.py makemigrations --env $ENV"
  python manage.py makemigrations --env $ENV
  echo -e "\nrunning python manage.py migrate --env $ENV"
  python manage.py makemigrations backend_django --env $ENV
  echo -e "\nrunning python manage.py migrate --env $ENV"
  python manage.py migrate backend_django --env $ENV
  echo -e "\nrunning python manage.py migrate --env $ENV"
  python manage.py migrate --env $ENV
fi

if [ $DEBUG -eq 1 ]; then
  echo -e "\nrunning python manage.py runserver"
  exec backend_django.asgi:application --reload --reload-include *.* --reload-dir ./backend_django --log-level info --env-file $ENV --host 0.0.0.0 --port 8000
fi

exec gunicorn --bind 0.0.0.0:8000 backend_django.asgi --reload --forwarded-allow-ips="*" --env MODE="$ENV"  --capture-output  -k uvicorn.workers.UvicornWorker --workers 16 --threads 16 --timeout 12000