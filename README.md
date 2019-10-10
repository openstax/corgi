# Workflow Service

## Requirements

* Docker and Docker Compose

## Local Development

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

## Migrations

Automatic migration files can be generated for the database. After a change is made you'll want to create a new revision.

Enter the backend Docker container:

    docker-compose exec backend bash

Create a revision:

    docker-compose exec backend alembic revision --autogenerate -m "added new column X"

A new revision will be added in the [migration](./backend/app/migrations/versions) folder.

Open the file and ensure the changes are what you expect.

Do the migration:

    docker-compose exec alembic upgrade head

## Attribution

A lot of the structure and ideas for this service come from Tiangolo's [full-stack-fastapi-postgres](https://github.com/tiangolo/full-stack-fastapi-postgresql) project. Thanks Tiangolo!
