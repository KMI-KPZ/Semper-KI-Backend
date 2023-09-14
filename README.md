# Backend for SEMPER-KI

## branch descriptions:
- **feature**: small changes, may not be a working state
- **dev**: bigger changes, has to work, for /dev domain
- **main**: major changes, production branch, has CI and CD

^^ will be changed in the future

## installation for dev purposes

- clone the repository
- checkout main|dev|feature branch
- run ```python manage.py generate_env``` to output an example env file which you can copy into .env.local_container
- edit .env.local_container for the external services (ask the team for credentials)
- run ```start_local_dev.sh -m local_container or start_local_dev.bat -m local_container ``` to build and run the containers
- a database will be created too
- if you want to develop locally instead of in a container run ```start_local_dev.sh -m local or start_local_dev.bat -m local ``` to start the backend locally
- stop all containers with ```stop_local_dev.sh or stop_local_dev.bat```


- the other environments will be added later