## Quick Start to Docs

For our COPS documentation we use [Sphinx](https://docs.readthedocs.io/en/stable/intro/getting-started-with-sphinx.html)

Get the project up from the root directory, if you haven't already with:
```
docker-compose up -d
```

When up, you should be able to visit localhost:8000 to see the docs

## Editing The Docs

Edits are done in restructured text (rst). 

Validate and update edits by running:
```
make html
```

If Navigations edits do not update, re-build the docker image.=:
```
$ cd output-producer-service
$ docker-compose down
$ docker-compose up
```

Note: Can be done in container or outside the container, with installed requirements.