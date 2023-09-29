#!/bin/bash
docker-compose --env_file .env.local_container -f dc-local-dev-services.yml -f dc-local-dev-container-backend.yml down