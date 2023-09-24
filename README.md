# goal_connect

FastAPI project for managing your goals and tasks.

## Description

goal_connect is an API built with FastAPI that allows users to create goals, add tasks to them, and more. This project provides a convenient interface for managing your goals and tracking their progress.

## Want to use this project?

Build the images and spin up the containers:

```sh
$ docker-compose up -d --build
```

Apply the migrations:

```sh
$ docker-compose exec fastapi alembic upgrade head
```

## Docs

You can find docs by this address: [127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)