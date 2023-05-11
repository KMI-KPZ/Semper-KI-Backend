# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8-slim-buster

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging when set to 1
ENV PYTHONUNBUFFERED=1

# Install psycopg2
RUN apt-get update \
    && apt-get -y install libpq-dev gcc bash \
    && pip install psycopg2
# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app

# RUN chmod +x app/backend_django/*.sh

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend_django.asgi", "--reload", "--capture-output", "--log-level", "debug", "--env", "DJANGO_SETTINGS_MODULE=backend_django.settings.development", "-k", "uvicorn.workers.UvicornWorker", "--workers",  "16", "--threads", "16"]
