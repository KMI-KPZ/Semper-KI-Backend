# Backend for SEMPER-KI

## branch descriptions:
- **feature**: small changes, may not be a working state
- **dev**: bigger changes, has to work, for /dev domain
- **main**: major changes, production branch, has CI and CD

## installation for dev purposes

- clone the repository
- checkout main|dev|feature branch
- specify which settings you want to use (on bash): 
    - for debugging: ```export DJANGO_SETTINGS_MODULE=backend_django.settings.debug```
    - for debug_local: ```export DJANGO_SETTINGS_MODULE=backend_django.settings.debug_local```
    - for production: ```export DJANGO_SETTINGS_MODULE=backend_django.settings.production```
    - for development: ```export DJANGO_SETTINGS_MODULE=backend_django.settings.development```
- generate an example env file via ```python manage.py generate_env``` and put the contents into a file named '.env' , fill it with your data (ask the team for credentials)
- 
