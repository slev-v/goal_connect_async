# Goal connect

FastAPI project for managing your goals and tasks.

## Description

Goal connect is an Async Web API built with FastAPI + SQLAlchemy 2.0. It includes asynchronous DB access using Asyncpg and test code covering them. With this project, you can efficiently manage your goals and tasks.

## Installation

### Environment Variables

First of all you need to create .env file in root project directory

```env
POSTGRES_DB=goal_connect
POSTGRES_USER=postgres
POSTGRES_PASSWORD=sliva
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

JWT_SECRET=your_secret_key
JWT_EXPIRE_MINUTES=6000
JWT_ALGORITHM=HS256
```

### Docker

To use Docker for running the project, make sure you have Docker and Docker Compose installed.

**Build the images and spin up the containers:**

```sh
$ docker compose up -d --build
```

**Apply the migrations:**

```sh
$ docker compose exec fastapi alembic upgrade head
```

### Local

Before getting started, make sure you have the following dependencies installed:

- Python
- Poetry (for managing project dependencies)

**Install dependencies**

```sh
$ poetry install
```

**Activate env**

```sh
$ poetry shell
```

**Make migrations**

```sh
$ alembic upgrade head
```

**Run uvicorn server**

```sh
$ uvicorn app.main:app --host 0.0.0.0 --port 8000
```


## Environment Variables

Here's what each environment variable in the .env file represents:

- POSTGRES_DB: Name of the PostgreSQL database.
- POSTGRES_USER: PostgreSQL username.
- POSTGRES_PASSWORD: PostgreSQL user's password.
- POSTGRES_HOST: PostgreSQL server host.
- POSTGRES_PORT: PostgreSQL server port.
- JWT_SECRET: Secret key for JWT authentication.
- JWT_EXPIRE_MINUTES: JWT expiration time in minutes.
- JWT_ALGORITHM: JWT encryption algorithm.


## Usage

You can find documentation by this link after running project [127.0.0.1:8000/docs](http:127.0.0.1:8000/docs)