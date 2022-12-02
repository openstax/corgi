# Content Output Review and Generation Interface (CORGI)

![CORGI](docs/_static/images/corgi.jpg)

_FKA: "CORGI", Content Output Review and Generation Interface_

---
- **What does CORGI do? 🤔**
  [Check out the high level docs](https://openstax.atlassian.net/wiki/spaces/CE/pages/2017918977/CORGI+Service)

- **I'd like to read the detailed docs 🤓**
  [Read The Docs](https://corgi.readthedocs.org/)

- **I'm ready to install and run CORGI 🚀**
  [Installation](#development-internals)

## Summary

The CORGI system consists of 2 parts:

1. CORGI Job Dashboard 
2. [Enki](https://github.com/openstax/enki) Pipeline

### CORGI Job Dashboard

The CORGI Job Dashboard or "CORGI dashboard" consists of a front-end microservice and a backend microservice. The CORGI Dashboard acts mainly as a "queue" of jobs to be processed by the Enki Concourse pipeline.

1. Backend - written using Python and the [FastAPI ASGI Framework](https://fastapi.tiangolo.com/). The backend API is used by the front-end and Enki pipelines to create, retrieve, or update job information. 

2. Frontend - written using [nuxt.js](https://nuxtjs.org/) and acts as the main dashboard interface of the CORGI system. You can see the list of jobs, create jobs, or abort a job that's in progress. Shows information pertaining to errors and status.

### [Enki](https://github.com/openstax/enki)

Enki produces the Concourse pipeline configuration files that are used to build book artifacts. Book artifacts can be pdf files, web preview links, docx, etc. Concourse uses "workers" that watch for new jobs created using the CORGI job dashboard. The Concourse pipeline reads the jobs from the CORGI backend and updates the job status and upon completion updates the job with links to the respective book artifact that was produced.

The full explanation of Enki it is out of scope for this documentation. To learn more please reference the [Enki README.md](https://github.com/openstax/enki/blob/main/README.md) within the project.

---
## Development Internals

### Installing Docker 

* Install [Docker](https://docs.docker.com/install/).

* Install [Docker Compose](https://docs.docker.com/compose/install/).

> **A note for Mac and PC users**
> After installing Docker, navigate to the Docker Desktop GUI preferences and increase the `Memory` value to at least `8GiB`.
> [Here's where you can find the Docker Desktop GUI settings](https://docs.docker.com/docker-for-windows/#resources)

### Local development

**Prerequisites**
* You will need access to a GitHub OAuth app. You can [create your own](https://docs.github.com/en/developers/apps/building-oauth-apps/creating-an-oauth-app) if you do not have one already.
* Create an env file, `backend/app/app/core/.env`, with three entries:
    1. `GITHUB_OAUTH_ID` (your oauth app client id)
    2. `GITHUB_OAUTH_SECRET` (your oauth app client secret)
    3. `SESSION_SECRET` (secret used to encrypt session cookies)

Build/start the stack with Docker Compose:

    docker-compose -f docker-compose.stack.dev.yml up -d

View the API Docs here:

* http://localhost/docs (Swagger)
* http://localhost/redoc (ReDoc)

To check the logs run:

    docker-compose logs backend/frontend/etc.


Using the development stack, the Svelte frontend is rebuilt inside the container 
as you make changes: no restarts required. The page should reload automatically
as well.

NOTE: The dev frontend server can take a while to start up. You might get 502
responses at first: this is normal. Wait a few seconds and try again.


### View the Docs

For our documentation we use [Sphinx-docs](https://www.sphinx-doc.org/en/master/)
and lives in the [./docs](./docs) directory.

If you are currently running the entire stack you should be able to see the
documentation by visiting [http://localhost:8000](http://localhost:8000).

The documentation is configured to watch for changes and re-build the documentation.
This allows developers the ability to preview their documentation changes as they 
make them.

If you would like to run the documentation without the entire stack running you 
can do so by running:

    docker-compose up docs

### Editing The Docs

Edits are done in restructured text (rst). 

Validate and update edits by running:
```
$ cd docs
$ make html
```

If edits have been made to the Navigation and are not reflected, re-build the docker image:
```
$ cd $CORGI_ROOT_PATH
$ docker-compose down
$ docker-compose up
```

Note: Can be done in container or outside the container, with installed requirements.

### Run integration and UI tests 

To run the tests execute:

    ./scripts/tests.ci.sh

### How to develop UI tests

> :warning: WARNING :warning: This functionality does not currently work because of the replacement of Selenium with Playwright. We do plan to return the functionality to the backend-tests image 

It's useful to run the stack locally when developing UI tests. The same script above in `Run integration tests` section can be edited in order to support interactive testing.

In the [./scripts/tests.ci.local](./scripts/tests.ci.local) file comment out the last line. This will keep all the containers alive after running the tests. Then you can continue to develop your tests and not need to re-create the environment everytime. 

In order to view the browser first list all the containers for the docker-stack.yml file:

    $ docker-compose -f docker-stack.yml ps

A table will be displayed with column names. Find the one labeled PORTS for the backend-tests container.

    PORTS
    4444/tcp, 0.0.0.0:32778->5900/tcp

Use a VNC application to connect to `0.0.0.0:32778`. The port number `32778` may be different.
The password for the VNC session is `secret`.
### Clear the database

Start the stack as described above

Run the reset-db command that is contained in the `manage.py` file.

    docker-compose exec backend python manage.py reset-db

### Migrations

Automatic migration files can be generated for the database. After a change is made you'll want to create a new revision.

Make sure the stack is running in development mode.

Enter the backend Docker container:

    docker-compose exec backend bash

Create a revision:

    docker-compose exec backend alembic revision --autogenerate -m "added new column X"

A new revision will be added in the [migration](./backend/app/migrations/versions) folder.

Open the file and ensure the changes are what you expect.

Do the migration:

    docker-compose exec alembic upgrade head

### Load testing for the backend

Load testing with Locust.io is in the directory `./backend/app/tests/performance/`

Please look at the [README](./backend/app/tests/performance/README.md) in this directory on how to run load tests locally and for production systems.
## Releasing

The documentation is located in the [Releasing CORGI article]((https://openstax.atlassian.net/wiki/spaces/CE/pages/1256521739/Releasing+CORGI)) in our Confluence documentation.

## Deploying Web Hosting Pipeline

The documentation is located in the [How to Deploy Web Hosting Pipeline article](https://openstax.atlassian.net/wiki/spaces/CE/pages/573538307/Deploying+the+web-hosting+pipeline) in our Confluence Documentation.
## Attribution

A lot of the structure and ideas for this service come from Tiangolo's [full-stack-fastapi-postgres](https://github.com/tiangolo/full-stack-fastapi-postgresql) project with additional supporting software and ideas from [authlib](https://docs.authlib.org/en/latest/client/fastapi.html). Thanks Tiangolo and Authlib devs!

## Login with GitHub Personal Access Token (PAT)
For situations where it is difficult or impossible to login with a username and password, there is an alternative way to login with a GitHub PAT. To utilize this functionality:

**Note:** the same restrictions apply to users regardless of login method (i.e. you do not gain additional permissions by logging in with a token).

1. Create a GitHub PAT with at least the `read:user`, `read:org`, and `repo` scopes.
2. Make a request to `/api/auth/login` with an additional header: `Authorization: Bearer <your-token>`
3. Get the session cookie from the `set-cookie` header in the response.
4. Make additional response with the session cookie.

### Example

```python
import os
import requests

# Note: This example assumes you are running CORGI locally

my_token = os.environ["TOKEN"]  # Don't hardcode secrets ;)

response = requests.get(
    "http://localhost/api/auth/login",
    headers={"Authorization": f"Bearer {my_token}"})

cookie = response.headers.get("set-cookie")
assert cookie is not None, "Could not get session cookie"

# Now you can use the cookie to make requests that require
# a valid user session
jobs = requests.get("http://localhost/api/jobs",
                    headers={"Cookie": cookie})
```
