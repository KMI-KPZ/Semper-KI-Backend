#  Semper-KI: Backend

<p align="center">
  <a href="https://semper-ki.org/">
    <img src="./doc/readme_kiss_logo.png" alt="kiss-logo" width="130" height="130">
  </a>
</p>



## 🔍 Project Overview

### Short Description

The Semper-KI acts as a platform where users can submit their 3D printing requirements and find suitable service providers. 
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
To run the application, you can use our `Docker Compose` starting script in the root of the project.
The script starts both the services and the backend inside Docker containers.

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

Note for Linux users:
- Verify that the Python 3.11 development headers are installed
```
sudo apt-get install python3.11-dev
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

<details><summary><strong>Optional commands</strong></summary>

- **Generate Example .env File:**
Outputs an example .env file with default values. Use -p --env to see the current values used by Django.
```
python manage.py generate_env 
```

- **Create Database:**
Creates the database specified in the environment. (Currently, the database name should be "local".)
```
python manage.py create_db --env <environment> 
```

- **Check Environment Health:**
Verifies that configuration parameters are set correctly, and ensures that both the database and Redis are reachable.
```
python manage.py check --env <environment>
```

- **Send Test Email:**
Sends a test email to the address configured for the environment.
```
python manage.py mail --env <environment> 
```
</details>

### Connection to Frontend
The Semper-KI Backend is designed to connect to the [Semper-KI Frontend](https://github.com/KMI-KPZ/Semper-KI-Frontend). Please refer to the documentation of the Semper-KI Frontend for instructions on how to set up and configure the frontend.


### Docker files
- `Dockerfile`: Used by local docker-compose files, uses caching for faster builds
- `Dockerfile.Server`:  Used for compose files that run on a server (no caching for example)

**Docker Compose files:**
- `docker-local-dev-container-backend.yml`: For the backend container when running in local_container mode
- `docker-local-dev-services.yml`: Every other container like redis, postgres and so on for local use
- `docker-compose.test.yml`: For running the tests, can be called via docker-compose up directly (used by GitHub Actions)
- `docker-compose.staging.yml`: Used on the server for staging
- `docker-compose.production.yml`: Same as above albeit for production


### 🗃️ Folder structure
<details> <summary>Click here to expand</summary>

```
.                      # Root directory
├── .devcontainer      # JSON config for running service containers and debug container
├── .github            # GitHub Actions workflows (CI/CD)
├── .vscode            # VSCode debug configuration
├── Benchy             # Tool for firing API calls
├── code_SemperKI      # Main application code
│   ├── connections    # External/internal service connections (Postgres, OpenAI, etc.)
│   │   └── content    # The session interface 
│   │       └── postgresql  # Postgres interface
│   ├── handlers       # API endpoints (only interfaces, no logic)
│   │   ├── private    # Internal-only APIs
│   │   └── public     # Public APIs (e.g. called by Frontend)
│   ├── logics         # Business logic tied to handlers
│   ├── migrations     # Django database migrations
│   ├── modelFiles     # Database interfaces and models
│   ├── services       # All platform services (example: Additive Manufacturing)
│   │   └── service_AdditiveManufacturing   # General stuff that every service has to provide 
│   │       ├── connections                 # Same as in Semper-KI but now for this service in particular 
│   │       │   └── postgresql              # Since this service has their own models, it needs a connection to the db
│   │       ├── handlers                    # API Paths of this service 
│   │       │   └── public                  # Only public paths available
│   │       │       └── resources           # Paths specific to the resource page of the platform
│   │       ├── logics                      # Logics of the handlers
│   │       ├── modelFiles                  # Models of the service
│   │       ├── tasks                       # Tasks that can be run in the background
│   │       └── utilities                   # Helper functions
│   ├── settings       # Django settings
│   ├── SPARQLQueries  # (Deprecated) SPARQL queries (Coypu project)
│   │   └── Coypu      # Queries specific to the Coypu service (deprecated)
│   ├── states         # Semper-KI state machine
│   ├── tasks          # Background tasks
│   ├── templates      # HTML templates
│   └── utilities      # Helper functions
├── doc                # Backend documentation
├── docker             # Docker scripts for Redis, MinIO
├── Generic_Backend    # Generic backend (included as submodule)
│   ├── code_General   # Main backend source code
│   ├── .vscode        # Debug configuration (not used here)
│   ├── configs        # Auth0 configuration
│   ├── connections    # DB connections and other services
│   │   └── postgresql # Postgres connection
│   ├── handlers       # Generic API endpoints
│   ├── logics         # Logic for generic handlers
│   ├── migrations     # Django migrations
│   ├── modelFiles     # Model files for the generic backend
│   ├── settings       # Settings (not used here)
│   ├── templates      # HTML templates
│   └── utilities      # Helper functions
├── logs               # Logfiles
├── main               # Main Django app
│   ├── helper         # Helper utilities (e.g. connection checks)
│   ├── management     # Local command line tools
│   │   └── commands   # Custom Django management commands
│   └── settings       # Main backend settings
├── minio              # Locally saved MinIO files
├── MSQ                # Message Queue for Celery tasks
│   ├── handlers       # Handlers for Celery workers
│   ├── module         # Celery module
│   └── tasks          # Celery tasks
│       └── scripts    # Scripts for Celery workers
├── Ontology           # (Unused) Ontology submodule
├── postgres           # Local database storage
├── redis              # Redis snapshots
└── run                # Run scripts
```
</details>

### Documentation
If backend is running: 
- Project Documentation: Available at [`http://127.0.0.1:8000/private/doc`](http://127.0.0.1:8000/private/doc)
- Swagger UI (API reference): Available at [`http://127.0.0.1:8000/public/api/schema/swagger-ui/`](http://127.0.0.1:8000/public/api/schema/swagger-ui/)


### Branch descriptions:
- **dev**: Where all branches derive from and will be pushed to
- **staging**: Intermediate between dev and production to test stuff in a live environment before pushing it to main, has CI/CD
- **main**: production branch, only pull requests from staging go here, has CI/CD


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



