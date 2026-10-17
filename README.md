<div align="center">

![Meridian](./banner.png)

# Meridian

[![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141.1-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLModel](https://img.shields.io/badge/SQLModel-0.0.39-0F172A)](https://sqlmodel.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-8-DC382D?logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

Meridian is an authentication and user-management API built with FastAPI. It uses PostgreSQL for persistent data and Redis for caching.

<div align="center">

![Database schema](./erd.png)

</div>

## Run with Docker Compose

You will need Docker and the Docker Compose plugin.

1. Clone the repository and enter the project directory:

   ```bash
   git clone https://github.com/Valentins-Jermakovs/Meridian.git
   cd Meridian
   ```

2. Create the environment file:

   ```bash
   cp .env.example .env
   ```

   Set private values for `POSTGRES_PASSWORD`, `JWT_SECRET_KEY`, and `PGADMIN_DEFAULT_PASSWORD`. Leave `REDIS_PASSWORD` empty; Redis is not configured with a password in the Compose file.

3. Create the external Docker network (skip this if it already exists):

   ```bash
   docker network create back_end
   ```

4. Build and start the services:

   ```bash
   docker compose up --build -d
   ```

The API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs). pgAdmin is available at [http://localhost:5050](http://localhost:5050), using the credentials in `.env`.

Stop the services with:

```bash
docker compose down
```
