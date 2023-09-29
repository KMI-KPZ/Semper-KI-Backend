# Backend for SEMPER-KI

## branch descriptions:
- **feature**: small changes, may not be a working state
- **dev**: bigger changes, has to work, for /dev domain
- **main**: major changes, production branch, has CI and CD

^^ will be changed in the future

## environments
the backend currently supports the environment "--env <environment>" which will be interpreted as follows:
- django settings file backend_django.settings.<environment>.py will be used
- .env.<environment> will be used for the environment variables
- if the environment MODE=<environment> is set, in asgi application it will work as on ```python manage.py command --env <environment>``` has been set (used for backend docker container)

## installation for dev purposes
(hint: on windows use the .bat version on linux the .sh version)

- clone the repository
- for clean initialization check that postgres folder is empty as well as redis folder
- run ```python manage.py generate_env``` to output an example env file which you should copy into project root folder .env.local_container
- edit .env.local_container for the external services (ask the team for credentials) and change ENV_TOKEN to local_container to see which env file is being used in outputs
- copy .env.local_container to .env.local and change internal services hosts (e.g. database, redis) to localhost as well as ENV_TOKEN to local to see which env file is being used in outputs
- run ```start_local_dev.sh -m local ``` to build and run the containers with background services (database, redis, celery)
- run ```python manage.py create_db --env local``` to create the database named in .env.local (which should be the same as in .env.local_container)
- run ```python manage.py migrate --env local``` to migrate the database to the latest state
- now you can run ```python manage.py runserver --env local``` to start the backend locally and edit
- or you can run all in a container (including the backend) with ```start_local_dev.sh -m local_container``` 
- or use VC-Code and RUN->Start Debugging ...beforehand stop all containers with ```stop_local_dev.bat``` the .env.local_container file will be used

watch exposed ports of the docker containers for services i.e. pg-admin (email/pw is in dc-local-dev-services.yml)

## commands
- ```python manage.py generate_env``` to output an example env file with default values, use with "-p --env <environment>" to get see the values currently used in django
- ```python manage.py create_db --env <environment>``` to create the database named in <environment> - which for now should be "local"
- ```python manage.py check --env <environment>``` to check if the parameters are set, the database can be reached, redis can be reached

- the other environments will be added later as well as the docker-compose files

## !! ATTENTION !! -> not yet ready for stage and production!