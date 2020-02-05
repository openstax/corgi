## Bakery Concourse Pipeline Generator

### Setup
- Install NodeJS and `yarn` on your machine.
- Ensure `bakery/` is your working directory.
- Run `yarn install` or `yarn`.

### Generate a pipeline file for a particular environment
- Run `yarn build:<env>`

  Available environments: `local`, `staging`, `prod`

  Example: `yarn build:staging`

  Note: Directory for output path must exist. If no path argument is given, the pipeline will output to `pipeline.yml` in the current working directory.

### Development
- There is no test suite in this repo, but a `yarn lint` command is provided to lint your work. This project uses `standard` to lint.
- Recommended way to verify your work is to go to the `output-producer-service` repository, start the `docker-compose` services in dev mode, and set-pipeline on the included concourse instance with a generated file by this repository.