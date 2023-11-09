@echo off
setlocal enabledelayedexpansion

echo Usage: start_local_dev.bat -m local_container or local
echo    local_container: starts services and backend in a local Docker container
echo    local: starts local services, and you can run the backend locally via "python manage.py runserver"

:parse_args
if "%~1" == "" (
    goto :end
)

if "%~1" == "-m" (
    set "MODE=%~2"
    shift
    shift
) else (
    echo Error: Wrong mode. Please use -m local_container or local
    goto :end
)

goto :parse_args

:end
if "%MODE%" == "local_container" (
    echo Starting services and backend in local container
    docker compose --env-file .env.local_container -p semperki-local-dev -f dc-local-dev-services.yml -f dc-local-dev-container-backend.yml up -d --no-deps --build backend
    docker compose --env-file .env.local_container -p semperki-local-dev -f dc-local-dev-services.yml -f dc-local-dev-container-backend.yml up -d
    echo Local containers started
) else if "%MODE%" == "local" (
    echo Starting local services
    docker-compose -p semperki-local-dev -f dc-local-dev-services.yml up -d
    echo Local started
)
