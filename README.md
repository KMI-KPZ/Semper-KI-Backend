#  Semper-KI: Backend

<p align="center">
  <a href="https://semper-ki.org/">
    <img src="doc/README_KISS_logo.png" alt="kiss-logo" width="130" height="130">
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
- **Auth & Security**: Authlib, OAuth2
- **Database**: PostgreSQL
- **Caching**: Redis
- **Task Queue**: Celery (Redis as broker)
- **Storage**: MinIO
- **API Documentation**: Swagger UI (DRF Spectacular)
- **Testing & Debugging**: pytest, Django Test Framework
- **Deployment**: Gunicorn, Uvicorn, Nginx
- **Containerization**: Docker
- **AI & NLP**: OpenAI SDK, LlamaIndex
- **3D & Visualization**: cadquery, matplotlib, numpy
- **PDF & Document Parsing**: PyMuPDF, pdfplumber, reportlab
- **Geospatial**: geopy
- **Semantic Web**: SPARQLWrapper
- **Code Quality**: Pylint


## 📚 Table of Contents

1. [Getting Started](#-Getting-Started)
2. [Development](#-Development)
3. [Deployment](#-Deployment)
4. [Best Practices](#-Best-Practices)
5. [Testing](#-Testing)
6. [Important Components](#-Important-Components)
7. [License](#-License)


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
  - You can check the .env template `exampleEnv.txt` and fill it out yourself

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


You may also need to do some configuring of the services used by the backend. See [Important Components](#-Important-Components) for more details.

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
See [CodeStyle.md](./CodeStyle.md) for the code style used in this project.


### Linting and Formatting
A `.pylintrc` configuration file is located in the main folder and can be used with the **Pylint** extension in VS Code.
This ensures consistent linting across the project.

### Recommended VSCode Extensions

- Pylint
- Docker
- Dev Containers
- GitHub Actions
- Python
- Pip Manager

## 🔧 Testing
### Running Tests
To run the tests, start the Docker containers using the `docker-compose.test.yml` file and look at the logs of the backend container to find errors. Alternatively, start the local_container version, go inside the container (either with the interface or via `docker exec -it <container name>`), type `bash` to get a console and call `python manage.py --env local_container test`.

### Test files
- `code_SemperKI/tests.py`: Contains all tests for the Semper-KI Part of the backend
- `code_SemperKI/services/service_AdditiveManufacturing/tests.py`: Contains all tests for the Additive Manufacturing Service
- `Generic_Backend/tests.py`: Contains all tests for the Generic Backend

## 📌 Important Components
### FEM Analysis
The platform contains a finite element simulation tool designed for 3D mechanical testing of arbitrary geometries described via STL files. It simulates simple compression or tension tests by automatically meshing the geometry and solving a linear elasticity problem. Please refer to [README_FEM.md](./code_SemperKI/services/service_AdditiveManufacturing/tasks/README_FEM.md) for more details.

### MinIO
[MinIO](https://min.io/) is used for object storage, providing a scalable and high-performance solution for storing files. It is compatible with the S3 API, making it easy to integrate with existing applications.
The backend can be run with an external S3 storage as well as with MinIO. To use the latter, some environment variables need to be set in the `.env.` files and a few folders need creating:

- Start the service via `docker-compose.local-dev-services.yml` or the `start_local_dev` script
- Open [http://127.0.0.1:9001](http://127.0.0.1:9001) and log in with the credentials set in the `.env` file
- Create a bucket called `kiss` and set the access policy to `public` with anynmous access set to read-only
  - Create a new path inside that bucket named `kiss` as well
  - Inside that path, the `ModelRepository` folder can to be created should you have one (this is not necessary for the backend to run but could be useful)
  - Upload some empty txt file or something, otherwise MinIO will delete the folder right away
- Create a bucket named `static` and set the access policy to `public` with anynmous access set to read-only
  - Create a new path inside that bucket named `public`
  - Inside that path, create two folders, `media` and `previews`
  - `media` should hold the icons for the services as well as placeholders like the KISS_logo and such (see [mediaConfig.json](./code_SemperKI/mediaConfig.json))
  - `previews` holds the preview images for the uploaded 3D models

### Knowledge Graph
The platform utilizes a knowledge graph to represent and manage the relationships between different entities in the 3D printing domain like printers, materials, colors, etc. They are called resources and are stored in the database. The knowledge graph is designed to be extensible, allowing for the addition of new resources and relationships as needed. It serves as a foundation for the platform's search and matching capabilities, enabling users to find relevant service providers based on their specific requirements.
To load in a test graph, use the endpoint `public/api/graph/loadTestGraph/` together with an authorization via an admin-level API token (via Swagger for example). The API Token can be generated by logging in as an admin, navigating to the end of the profile settings and clicking on `Create`. The whole graph can be seen visually in the admin panel.

### Read PDFs into the Knowledge Graph
The platform can read PDFs of printers and materials and extract relevant information to populate the knowledge graph. This feature is particularly useful for extracting data from technical documents, specifications, and other resources related to 3D printing. It requires an OpenAI API key saved into the respective entries in the `.env` files. The two API calls used for this are `public/api/extractFromPDF/` and `public/api/extractFromJSON/`. The former can first create a JSON file from the PDF and then extract the information from it. The latter can be used to extract information from a JSON file that has been created by the first API call (should post-processing of the information be needed and believe me, it usually is!). The extracted information is then stored in the knowledge graph, making it accessible for search and matching purposes.

### Auth0/Oauth
The platform uses Auth0 for authentication and authorization allowing users to log in using their existing accounts from various identity providers (e.g., Google, Facebook) or create their own. The necessary credentials must be stored in the `.env` files as well as in the `configs/auth0.json` file of the `Generic_Backend` submodule where applicable. You also need to create a Default role and store the role ID in the `.env` files and the config file as well as the role "semper-admin" for admins with all permissions. Regarding permissions: An Auth0 API for permissions is needed as well and inside it, the following permissions must be created:
- orga:read	(read organization details)	
- orga:edit	edit (organization details)
- resources:edit	(edit resources for orga)	
- resources:read	(read resources from orga)	
- orga:delete	(Delete organisation)
- processes:read	(Read processes and projects)	
- processes:messages	(Messages in processes)
- processes:edit	(Edit processes and projects)
- processes:delete	(Delete processes and projects)	
- processes:files (Upload and Download files)
  
In short, we configured the Applications like this: 
- Users: Settings: Regular Web Application, Allowed Callback/Logout URLs and Allowed Web Origins with our urls, Advanced: Implicit, Authorization Code and Refresh Token, Credentials: Client Secred (Post), Organizations: Both, No Prompt
- Organizations: Settings: Regular Web Application, Application Login URI with out redirect routine of the frontend, Allowed Callback/Logout URLs and Allowed Web Origins with our urls, Advanced: Implicit, Authorization Code and Refresh Token, Credentials: Client Secred (Post), Organizations: Business Users, Prompt for Credentials
- API calls: Settings: Machine to Machine, Advanced: Client Credentials, Credentials: Client Secred (Post), APIs: Auth0 Management API with permissions to client_grants, users, users_app_metadata, user_custom_blocks, resource_servers, email_templates, roles, role_members, organizations_summary, organizations, organization_members, organization_connections, organization_member_roles, organization_invitations; Permissions API authorized but no permissions given
  
We also created some Actions, one where we added the claims to the token during login: 
``` 
exports.onExecutePostLogin = async (event, api) => {
  const namespace = 'https://auth.semper-ki.org/claims';
  if (event.authorization) {
    api.idToken.setCustomClaim(`${namespace}/roles`, event.authorization.roles);
    api.accessToken.setCustomClaim(`${namespace}/roles`, event.authorization.roles);
  }
  if (event.organization) {
    api.idToken.setCustomClaim(`${namespace}/organization`, event.organization.display_name);
  }
} 
```
And one where we set the user language:
```
exports.onExecutePreUserRegistration = async (event, api) => {
  const inputLanguage = event.transaction.ui_locales[0]
  let userLanguage = 'de-DE';  // Default to 'de-DE'

  if (inputLanguage === 'en-EN') {
    userLanguage = 'en-EN';
  }

  api.user.setUserMetadata("language", userLanguage);
};
```


## 📜 License

This project is licensed under the [Eclipse Public License 2.0 (EPL-2.0)](https://www.eclipse.org/legal/epl-2.0/).

You are free to use, modify, and distribute this software, provided that you comply with the terms of the license.

For more details, see the [LICENSE](./LICENSE) file in this repository.



