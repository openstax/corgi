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

## Container Cluster creation and deployment for dev work

A set of 3 servers that have been setup as docker swarm master nodes.

* https://cc1.cnx.org
* https://cc2.cnx.org
* https://cc3.cnx.org

### Initial setup of the cluster

Create the networks

```bask
docker network create --driver overlay pdf-spike-backend
```

Set some important tags on the nodes

```bash
docker node update --label-add db=true cc1.cnx.org
```

Create the db

```bash
docker service create --name db --constraint-add 'node.labels.db == true' --mount type=volume,source=db-data,target=/var/lib/postgresql/data --network pdf-spike-backend postgres:11
```

Create the backend

```bash
docker service create --name pdf-spike-backend --network pdf-spike-backend --label traefik.frontend.rule=PathPrefix:/api,/docs,/redoc --label traefik.enable=true --label traefik.port=80 --replicas openstax/pdf-spike-backend
```

Create the frontend

```bash
docker service create --name pdf-spike-frontend --network pdf-spike-backend --label traefik.frontend.rule=PathPrefix:/ --label traefik.enable=true --label traefik.port=80 --replicas 1 openstax/pdf-spike-frontend
```


### Deployment process for dev work

>Note: A lot of the process described below can be accomplished with the 
>[`docker stack`](https://docs.docker.com/engine/reference/commandline/stack/) 
>command. This approach isn't being utilized at the moment in order to allow 
>developers to become more familiar with the underlying `docker service` commands.


Currently, we don't use the docker stack command. The individual services for 
the system are created via exclusive usage of the 
[docker service create](https://docs.docker.com/engine/reference/commandline/service/) command.


Follow the build and push steps defined above except with a tag named after your PR.

**Example**

    TAG=my-changes ./scripts/build-push.sh

When the images have been deployed to hub.docker.com login to one of the container servers.

    ssh cc1.cnx.org

Depending on the frontend or backend image update the appropriate service.

**Backend**

    docker service update pdf-spike-backend --force --image openstax/pdf-spike-backend:my-changes

**Frontend**

    docker service update pdf-spike-frontend --force --image openstax/pdf-spike-frontend:my-changes

To restart a service you can set replicas to 0 and then back to any number.

    docker service update --replicas 0 pdf-spike-frontend

To start it back up

    docker service update --replicas 1 pdf-spike-frontend


## Attribution

A lot of the structure and ideas for this service come from Tiangolo's [full-stack-fastapi-postgres](https://github.com/tiangolo/full-stack-fastapi-postgresql) project. Thanks Tiangolo!
