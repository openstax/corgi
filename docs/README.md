## Quick Start to Docs

For our COPS documentation we use [Sphinx](https://docs.readthedocs.io/en/stable/intro/getting-started-with-sphinx.html)

Get the project up from the root directory, if you haven't already with:
```
docker-compose up -d
```

When up, you should be able to visit localhost:8000 to see the docs

## Editing the docs

Edits are done in restructured text. 

Validate and update your edits by running:
```
make html
```

Sometimes if edits don't take and the navigation doesn't update, re-build the docker image.



Note: In container or outside the container, with installed requirements. 

