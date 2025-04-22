#  Semper-KI: Backend

<p align="center">
  <a href="https://semper-ki.org/">
    <img src="doc/readmeKissLogo.png" alt="logo" width="130" height="130">
  </a>
</p>

## 🔍 Project Overview

### Short Description

The Semper-KI Frontend acts as a platform where users can submit their 3D printing requirements and find suitable service providers. 
It leverages artificial intelligence to optimize the matching process by considering factors such as material properties, printing technology, 
pricing, and delivery options. The user-friendly interface allows users to easily navigate, submit their requirements, and track order progress, 
streamlining the process of connecting supply and demand in the 3D printing industry.

### Live Demo/Preview

[Semper-KI Live Demo](https://semper-ki.org/)

(Note: This is a science project, and the demo may not be available later on.)

### Tech Stack

- **Language**: Python 3.11
- **Backend**: Django, Django REST Framework, Channels
- **Auth & Security**: Authlib, python-jose, PyJWT, social-auth-app-django
- **Database**: PostgreSQL
- **Caching**: Redis
- **Task Queue**: Celery (Redis as broker)
- **Storage**: MinIO, Amazon S3 (`django-storages`)
- **API Documentation**: Swagger UI (DRF Spectacular)
- **Testing & Debugging**: pytest, Django Test Framework
- **Deployment**: Gunicorn, Uvicorn, Nginx
- **Containerization**: Docker
- **AI & NLP**: OpenAI SDK, LlamaIndex
- **3D & Visualization**: cadquery, matplotlib, numpy
- **PDF & Document Parsing**: PyMuPDF, pdfplumber, reportlab
- **Geospatial**: geopy
- **Semantic Web**: SPARQLWrapper
- **Code Quality**: Pylint, Flake8


## 📚 Table of Contents

1. [Getting Started](#-Getting-Started)
2. [Development](#-Development)
3. [Deployment](#-Deployment)
4. [Best Practices](#-Best-Practices)
5. [License](#-License)


## 🚀 Getting Started

### Prerequisites

Make sure you have the following installed on your machine:

- `Docker`: Latest version
- (`Python`: 3.11)

### Environment Variables
Make sure you have the following `.env` file
- `.env.local_container`: For local development with Docker 


- If you don't have this .env file:
  - Ask the KISS team to send it to you
  - You can check the .env template `exampleEnv.txt`

### Installation

Clone the repository:

```bash
git clone git@github.com:KMI-KPZ/Semper-KI-Backend.git
cd Semper-KI-Backend
```

Install git submodules:
```bash
git submodule update --init
```



Optional:
- Install packages to your local machine
```
python -m pip install -r requirements.txt
```


### Running the Application
To run the application, you can use our `docker compose` starting script in the root of the project.
The Script starts both the services and the backend inside Docker containers.

#### Windows
```
start_local_dev.bat -m local_container
```

#### Linux/Mac
1. Make the script executable:
```
chmod +x start_local_dev.sh
```
2. Run the script
```
./start_local_dev.sh -m local_container
```

> **Note:**  
> The backend container supports hot reloading — changes to files are reflected automatically after saving.  
> In debug mode, the current request handler must complete before the worker restarts.  
> There may be a slight delay before the changes take effect, but the logs will indicate when the reload occurs.


## 🛠️ Development


### Run Backend Locally (Without Docker)
#### Prerequisites

Make sure you have the following installed on your machine:

- `Docker`: Latest version
- `Python`: 3.11

#### Environment Variables
Make sure you have the following `.env` file
- `.env.local`: For local development without Docker

#### Installation
Follow installation in [Getting Started](#-Getting-Started) (clone project and install submodules)

- Install packages to your local machine
```
python -m pip install -r requirements.txt
```

#### Services
- Run the services in Docker containers:

```bash
# Windows
start_local_dev.bat -m local

# Linux / macOS
chmod +x start_local_dev.sh
./start_local_dev.sh -m local
```

#### Database
1. Create the database:
```
python manage.py create_db --env local
```
2. Migrate the database to the latest state:
```
python manage.py migrate --env local
```
3. Run the backend locally:
```
python manage.py runserver --env local
```


### Connection to Frontend
The Semper-KI Backend is designed to connect to the [Semper-KI Frontend](https://github.com/KMI-KPZ/Semper-KI-Frontend). Please refer to the documentation of the Semper-KI Frontend for instructions on how to set up and configure the frontend.


### Docker files
There are a couple of docker and docker-compose files in the root folder. 
Regarding the docker files:
- `Dockerfile`: Used by local docker-compose files, uses caching for faster builds
- `Dockerfile.Server`:  Used for compose files that run on a server (no caching for example)

As for the compose files:
- `docker-local-dev-container-backend.yml`: For the backend container when running in local_container mode
- `docker-local-dev-services.yml`: Every other container like redis, postgres and so on for local use
- `docker-compose.test.yml`: For running the tests, can be called via docker-compose up directly, used by GitHub Actions
- `docker-compose.staging.yml`: Used on the server for staging
- `docker-compose.production.yml`: Same as above albeit for production


### 🗃️ Folder structure
- `.`: The main folder contains the manage.py file of django and docker files as well as the .env files
  - `.devcontainer`: Contains the json needed for running the service containers together with the debug container
  - `.github`: Contains the CI workflow used in GitHub Actions
  - `.vscode`: Everything necessary to run the debug-mode of VS Code
  - `Benchy`: A small tool to fire calls to certain paths
  - `code_SemperKI`: The main part of the software
    - `connections`: All connections to external and internal services like postgres, openai and such
      - `content`: The session interface
        - `postgresql`: The postgres interface
    - `handlers`: All API Paths that are specific to Semper-KI but not to the individual services it offers, only the API interface, no logics
      - `private`: API Paths only callable from the local environment
      - `public`: API Paths callable from outside (e.g. by the Frontend)
    - `logics`: The corresponding logics of the handlers
    - `migrations`: Django database migration versions
    - `modelFiles`: Database interfaces and models
    - `services`: All services that this platform offers, as a representative, see here the service "Additive Manufacturing"
      - `service_AdditiveManufacturing`: General stuff that every service has to provide
        - `connections`: Same as in Semper-KI but now for this service in particular
          - `postgresql`: Since this service has their own models, it needs a connection to the db
        - `handlers`: API Paths of this service
          - `public`: Only public paths available
            - `resources`: Paths specific to the resource page of the platform
        - `logics`: Logics of the handlers
        - `modelFiles`: Models of the service
        - `tasks`: Tasks that can be run in the background
        - `utilities`: Helper functions
    - `settings`: Django settings for this app
    - `SPARQLQueries`: Old folder that could have hold all relevant SPARQL queries
      - `Coypu`: Queries specific to the Coypu service (deprecated)
    - `states`: The statemachine of Semper-KI
    - `tasks`: Background tasks
    - `templates`: HTML Templates
    - `utilities`: Helper functions
  - `doc`: Documentation of the Backend
  - `docker`: Docker scripts for redis and minio
  - `Generic_Backend`: The generic backend, included here as a submodule
    - `code_General`: Main folder with source code
      - `.vscode`: Debug stuff, not used here
      - `configs`: Contains the auth0 configuration
      - `connections`: DB connections and such
        - `postgresql`: postgres connection
      - `handlers`: API Paths for generic purposes
      - `logics`: Logics of the paths
      - `migrations`: Migrations of django
      - `modelFiles`: Model files of the GB
      - `settings`: Settings, not used here
      - `templates`: HTML Templates
      - `utilities`: Helper functions
  - `logs`: Logfiles
  - `main`: Main django app
    - `helper`: Helper stuff like checking connections
    - `management`: Local command line tools
      - `commands`: 
    - `settings`: Main settings of the Backend
  - `minio`: Folder containing the locally saved files
  - `MSQ`: Message queue for celery tasks
    - `handlers`: Handlers for the celery workers
    - `module`: Celery module
    - `tasks`: The tasks themselves
      - `scripts`: Scripts that can be run by the workers
  - `Ontology`: Ontology submodule, not used
  - `postgres`: Folder that holds the database
  - `redis`: Folder that holds snapshots of redis
  - `run`: Run scripts

### Documentation
If backend is running: 
- Project Documentation: Available at [`http://127.0.0.1:8000/private/doc`](http://127.0.0.1:8000/private/doc)
- Swagger UI (API reference): Available at [`http://127.0.0.1:8000/public/api/schema/swagger-ui/`](http://127.0.0.1:8000/public/api/schema/swagger-ui/)


### Branch descriptions:
- **dev**: Where all branches derive from and will be pushed to
- **staging**: Intermediate between dev and production to test stuff in a live environment before pushing it to main, has CI and CD
- **main**: production branch, only pull requests from staging go here, has CI and CD


## 💾 Deployment

## CI/CD
When changes are committed to the `main` branch of the backend, the CI/CD pipeline is triggered. 

The process works as follows:
1. **GitHub Actions** automatically run tests using Docker Compose. This ensures that all tests execute in a consistent environment and pass successfully.
2. If the tests pass, a **webhook** event is sent to the server. If successful, the server pulls the latest commit and restarts the Docker containers in the production environment.

>  **Note:** Since the `.env.production` file is used by the test container, its contents must be stored securely in the GitHub secrets for the backend repository



## 🌟 Best Practices
### Clean Code
bla

### Naming
bla


### Linting and Formatting

A `.pylintrc` configuration file is located in the main folder and can be used with the **Pylint** extension in VS Code.
This ensures consistent linting across the project.

### VSCode Extensions

- pylintrc

#### WSL Extensions
bla

#### Local Extensions

bla


## 📜 License

This project is licensed under the [Eclipse Public License 2.0 (EPL-2.0)](https://www.eclipse.org/legal/epl-2.0/).

You are free to use, modify, and distribute this software, provided that you comply with the terms of the license.

For more details, see the [LICENSE](./LICENSE) file in this repository.



