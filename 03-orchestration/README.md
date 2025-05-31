# Orchestration Using Airflow 3.0

## Runing Airflow with Docker

Below is a **minimal, vanilla-Airflow 3.x workflow that runs completely in Docker Compose, no Astronomer required.**
I’m using `3.0.1` (the latest patch on top of the 3.0 GA released 22 Apr 2025), but you can pin to `3.0.0` the same way. ([Apache Airflow][1], [Apache Airflow][2])

---

## 1  Prerequisites

| Tool                  | Version (or newer)                                 | Why                                                                  |
| --------------------- | -------------------------------------------------- | -------------------------------------------------------------------- |
| **Docker Engine**     | 24.x                                               | container runtime                                                    |
| **Docker Compose v2** | (ships with Docker Desktop / `docker compose` CLI) | required features in the official YAML                               |
| **Memory**            | ≥ 4 GiB (8 GiB ideal)                              | the web-server will keep restarting if too low ([Apache Airflow][2]) |

---

## 2  Project scaffold

```bash
# Create a clean workspace
mkdir airflow3 && cd airflow3

# Grab the Compose file for Airflow 3.0.1 (or change the URL to 3.0.0)
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/3.0.1/docker-compose.yaml'

# Make the mounted folders Airflow expects
mkdir -p ./dags ./logs ./plugins ./config

# Set your host UID/GID (Linux only; macOS/Windows can skip)
echo "AIRFLOW_UID=$(id -u)" > .env
```

The YAML already points to the image
`apache/airflow:3.0.1` (see the `AIRFLOW_IMAGE_NAME` variable).

### 2.1 tweaking the yaml file

``` yaml
environment:
    &airflow-common-env
    AIRFLOW__CORE__EXECUTOR: CeleryExecutor  #change to : LocalExecutor 
    AIRFLOW__CORE__AUTH_MANAGER: airflow.providers.fab.auth_manager.fab_auth_manager.FabAuthManager
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
    AIRFLOW__CELERY__RESULT_BACKEND: db+postgresql://airflow:airflow@postgres/airflow #remove
    AIRFLOW__CELERY__BROKER_URL: redis://:@redis:6379/0 #remove
    AIRFLOW__CORE__FERNET_KEY: ''
    AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'true'
    AIRFLOW__CORE__LOAD_EXAMPLES: 'true' #channge to 'false'
```
  Remove redis and celery worker  
  change to build .  
  ```
  #image: ${AIRFLOW_IMAGE_NAME:-apache/airflow:3.0.1}
  build: .
  ```
### 2.2 Add Dockerfile


---

## 3  First-time initialise & start

```bash
# 1. Run DB migrations and create admin user (user/pass = airflow/airflow)
docker compose up airflow-init

# 2. Launch the full stack (scheduler, webserver, workers, etc.)
docker compose up
```

Open **[http://localhost:8080](http://localhost:8080)** → login **airflow / airflow**.

---

## 4  Hello-world DAG (new Airflow SDK syntax)

Create `dags/hello_world.py`:

```python
from datetime import datetime
from airflow.sdk import DAG, task   # 3.0’s stable authoring interface

with DAG(
    dag_id="hello_world",
    start_date=datetime(2025, 5, 30),
    schedule=None,          # manual run
    catchup=False,
    tags=["example"],
) as dag:

    @task
    def greet():
        print("👋  Hello from Airflow 3!")

    greet()
```

Save → the scheduler parses it in \~30 s; trigger it from the UI.

---

# 5 Homework
## Question 1
## Question 2

## Question 3
How many records did we load? 

- 3,003,766
- 3,203,766
- **3,403,766**
- 3,603,766

records: (3403766, 19): chan="stdout"

## Question 4. Data preparation
Let's apply to the data we loaded in question 3. 

What's the size of the result? 

- 2,903,766
- 3,103,766
- 3,316,216 
- 3,503,766
