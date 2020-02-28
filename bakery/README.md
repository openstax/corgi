## Bakery Concourse Pipeline Generator

### Setup
- Install NodeJS and `yarn` on your machine.

This project uses Yarn PnP.

### Usage
`build` is an executable that provides a small cli to build your concourse pipeline/task files. This is the help message returned by calling it with `./build --help`:
```
./build <command>

Commands:
  build.js pipeline <env> [options]...   builds the full bakery pipeline                          [aliases: p]
  build.js task <taskname> [options]...  builds a bakery pipeline task runnable with fly execute  [aliases: t]

Options:
  --help  Show help                                                                                  [boolean]
```

In general, for both the `pipeline` and `task` commands, the `--help` messages are fairly useful and complete. That is:

`./build pipeline --help`

and

`./build task --help`

will provide information about the command, defaults, and its positional and nonpositional arguments.

### Generate a pipeline file for a particular environment
Run `./build pipeline <env> [options]...`

The choices for `<env>` are the basenames of the `.json` files in the `env/` directory.

Examples:
- `./build pipeline prod` -> Build the pipeline with prod environment variables and output on stdout.
- `./build pipeline staging -o pipeline.staging.yml` -> Build the pipeline with staging environment variables and output to file `pipeline.staging.yml`, overwriting the file if it exists.

### Generate a standalone task file suitable for `fly execute`
Run `./build task <taskname> [options]...`

The choices for `<taskname>` are the basenames of the `.js` files in the `src/tasks/` directory.

Example:
- `./build task look-up-book -a "{bucketName: my-bucket}"` -> Build the look-up-book task, injecting the object `{bucketName: "my-bucket"}` as the argument to the task function, and output the result to stdout
- `./build task fetch-book -o fetch-book-task.yml` -> Build the fetch-book task, and output the result to the file `fetch-book-task.yml`

Note: The `--args` option (shorthand, `-a`) must be valid `yaml` (or `json`, since yaml is a superset).

### I don't like generating intermediate files to run `set-pipeline` or `execute`!
Use process substitution!
Example: `fly -t dev sp -p bakery -c <(./build pipeline staging)`

### Development
- There is no test suite in this repo, but a `yarn lint` command is provided to lint your work. This project uses `standard` to lint.
- Recommended way to verify your work is to go to the `output-producer-service` repository, start the `docker-compose` services in dev mode, and set-pipeline on the included concourse instance with a generated file by this repository.