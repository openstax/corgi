# Workflow Service

## Requirements

Follow the instructions to install [Docker](https://docs.docker.com/install/).

Follow the instructions to install [Docker Compose](https://docs.docker.com/compose/install/).

## Architecture

The workflow-service contains of two parts:

1. Backend
2. Frontend

The backend is written using Python and the FastAPI ASGI Framework 

## Backend local development

Start the stack with Docker Compose:

    docker-compose up -d

View the API Docs here:

http://localhost:5001/docs

To check the logs run:

    docker-compose logs

## Live Development with Jupyter Notebooks

Enter the backend Docker container:

    docker-compose exec backend bash

Run the environment variable `$JUPYTER` which is configured to be accessible via a public port http://localhost:8888

    $JUPYTER

A message like this should pop up:

```bash
    Copy/paste this URL into your browser when you connect for the first time,
    to login with a token:
        http://(73e0ec1f1ae6 or 127.0.0.1):8888/?token=f20939a41524d021fbfc62b31be8ea4dd9232913476f4397
```

You will have full Jupyter access inside your container that can be used to access your database.

### Migrations

Automatic migration files can be generated for the database. After a change is made you'll want to create a new revision.

Enter the backend Docker container:

    docker-compose exec backend bash

Create a revision:

    docker-compose exec backend alembic revision --autogenerate -m "added new column X"

A new revision will be added in the [migration](./backend/app/migrations/versions) folder.

Open the file and ensure the changes are what you expect.

Do the migration:

    docker-compose exec alembic upgrade head

## What's up with all the docker-compose files?

This takes a little getting used to initially but does make the management of the files much easier
when needing to reuse the same values in other environments. Eventually, it becomes quick to make edits
to the appropriate parts of the stack without muddling in other details.

This becomes more apparent in the [build and push](./scripts/build-push.sh) and the [deploy.sh](./scripts/deploy.sh) script.

Within these files we're able to pass in several docker-compose files and compile them into one file that is used for various things.

The only thing needed to alter some key values is the passing in of the appropriate environment variables.

## Pushing images to docker hub

Run the script [./scripts/build-push.sh](./scripts/build-push.sh) with the appropriate environment variables:

    TAG=latest FRONTEND_ENV=production ./scripts/build-push.sh

## Attribution

A lot of the structure and ideas for this service come from Tiangolo's [full-stack-fastapi-postgres](https://github.com/tiangolo/full-stack-fastapi-postgresql) project. Thanks Tiangolo!
