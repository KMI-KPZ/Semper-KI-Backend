# Backend for SEMPER-KI

## Branch descriptions:
- **dev**: Where all branches derive from and will be pushed to
- **main**: production branch, only pull requests from dev go here, has CI and CD
- **Form for your branches**: \<Your Name>/\<Ticket Number on Jira>/\<Topic>

## Environments
The backend currently supports the environment ```--env <environment>``` which will be interpreted as follows:
- django settings file ```code_General.settings.<environment>.py``` will be used
- .env.\<environment> will be used for the environment variables
- if the environment MODE=\<environment> is set, in asgi application it will work as on ```python manage.py command --env <environment>``` has been set (used for backend docker container)

## Good to know
- The Backend Container supports hot reloading, which means that editing files and saving changes will be reflected instantly. For the Debug Version, the current handler must be finished, then the worker will restart after saving the changes. The Container is a bit delayed but the logs show if and when it happend

## Installation for dev purposes
(hint: on windows use the .bat version on linux the .sh version)

- check, that you have at least Python 3.11 installed (via Terminal/Powershell and `python --version`) and correctly linked in your system environment variables (see: https://realpython.com/add-python-to-path/)
- clone the repository via SSH (in VS Code preferably)
- run ```git submodule init``` to initialize your local configuration file, and 
- run ```git submodule update``` to fetch all the data from that project and check out the appropriate commit listed in your superproject.
- for clean initialization check that postgres folder is empty as well as redis folder
- call ```python -m pip install -r requirements.txt``` to install packages to your local machine (optional)
- to run the backend, you need at least one ".env" file, either you ask your team to send it to you, or you can generate one yourself. To do the latter, do as follows:
  - call ```python manage.py generate_env``` to output how the env file should look (scroll down a bit). The output should be copied into a file lying in your project root folder. Name it .env.local_container
  - edit .env.local_container for the external connections (ask the team for credentials) and change ENV_TOKEN to local_container to see which env file is being used in outputs
  - copy .env.local_container to .env.local and change internal connections hosts (e.g. database, redis) to localhost as well as ENV_TOKEN to local to see which env file is being used in outputs
- create the folder `logs` if it doesn't exist in the root directory of the project, as well as the files `info.log` and `ip_log.log` inside it. Open your WSL/Terminal and call `sudo chown -R 5678 logs/` on it from the WSL
- call ```start_local_dev.bat -m local ``` to build and run only the containers with background connections (database, redis, ...)
- LOCAL ONLY: call ```python manage.py create_db --env local``` to create the database named in .env.local (which should be the same as in .env.local_container) 
- OR CONTAINER ONLY: launch the containerized version twice (first will create the db, second will use it)
- LOCAL ONLY: call ```python manage.py migrate --env local``` to migrate the database to the latest state 
- LOCAL ONLY: now you can call ```python manage.py runserver --env local``` to start the backend locally and edit 
- OR CONTAINER ONLY: or you can run all in a container (including the backend) with ```start_local_dev.bat -m local_container``` 
- OR DEBUG ONLY: use VS Code and RUN->Start Debugging but beforehand, stop all containers with ```stop_local_dev.bat```

INFO: you can watch exposed ports of the docker containers for connections i.e. pg-admin (email/pw is in docker-local-dev-services.yml)

INFO: The documentation can be seen via the private/doc path

## Debug logging
In order to have debug output in the console, in your .env.[MODE] file set ```DJANGO_LOG_LEVEL=DEBUG```.
To log your messages use ```getLogger("django_debug").debug("your message")```

## Docker files
There are a couple of docker and docker-compose files in the root folder. 
Regarding the docker files:
- `Dockerfile`: The main file with a default entry point. Used by almost all docker-compose files
- `Dockerfile.Testing`: Only used for running the tests and is coupled with the docker-compose.test.yml file.

As for the compose files:
- `docker-local-dev-container-backend.yml`: For the backend container when running in local_container mode
- `docker-local-dev-services.yml`: Every other container like redis, postgres and so on
- `docker-compose.test.yml`: For running the tests, can be called via docker-compose up directly
- `docker-compose.stage.yml`: Used on the server for staging
- `docker-compose.production.yml`: Same as above albeit for production

## Optional commands
- ```python manage.py generate_env``` to output an example env file with default values, use with "-p --env <environment>" to get see the values currently used in django
- ```python manage.py create_db --env <environment>``` to create the database named in <environment> - which for now should be "local"
- ```python manage.py check --env <environment>``` to check if the parameters are set, the database can be reached, redis can be reached
- ```python manage.py mail --env <environment> email-address``` to send a test mail to the email-address

- the other environments will be added later as well as the docker-compose files

## !! ATTENTION !! -> not yet ready for stage and production!

# Installation of Frontend

