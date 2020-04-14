const path = require('path')
const fs = require('fs')
const { execFileSync, spawn } = require('child_process')

const sleep = require('sleep')
const tmp = require('tmp')
tmp.setGracefulCleanup()

const completion = subprocess => {
  const error = new Error()
  return new Promise((resolve, reject) => {
    subprocess.on('exit', code => {
      if (code === 0) {
        resolve(undefined)
      } else {
        error.message = `Subprocess failed with code ${code}`
        reject(error)
      }
    })
  })
}

const input = (dataDir, name) => `--input=${name}=${dataDir}/${name}`
const output = (dataDir, name) => `--output=${name}=${dataDir}/${name}`

const composeYml = `
---
version: "3"

services:
  concourse-db:
    image: postgres
    environment:
      - POSTGRES_DB=concourse
      - POSTGRES_PASSWORD=concourse_pass
      - POSTGRES_USER=concourse_user
      - PGDATA=/database

  concourse:
    image: concourse/concourse:4.2.2
    command: quickstart
    privileged: true
    depends_on: [concourse-db]
    ports: ["8080:8080"]
    environment:
      - CONCOURSE_POSTGRES_HOST=concourse-db
      - CONCOURSE_POSTGRES_USER=concourse_user
      - CONCOURSE_POSTGRES_PASSWORD=concourse_pass
      - CONCOURSE_POSTGRES_DATABASE=concourse
      - CONCOURSE_EXTERNAL_URL
      - CONCOURSE_ADD_LOCAL_USER=admin:admin
      - CONCOURSE_MAIN_TEAM_LOCAL_USER=admin
`

const flyExecute = async cmdArgs => {
  const tmpComposeYml = tmp.fileSync()
  fs.writeFileSync(tmpComposeYml.name, composeYml)

  const children = []

  process.on('exit', code => {
    if (code !== 0) {
      children.forEach(child => {
        if (child.exitCode == null) {
          child.kill('SIGINT')
        }
      })
    }
  })

  const startup = spawn('docker-compose', [
    '-f', tmpComposeYml.name,
    'up',
    '-d'
  ], {
    stdio: 'inherit'
  })
  children.push(startup)
  await completion(startup)

  try {
    let retries = 0
    let success = false
    while (!success) {
      try {
        console.log('logging in')
        const login = spawn('fly', [
          'login',
          '-k',
          '-t', 'bakery-cli',
          '-c', 'http://127.0.0.1:8080',
          '-u', 'admin',
          '-p', 'admin'
        ], { stdio: 'inherit' })
        children.push(login)
        await completion(login)
        success = true
      } catch {
        if (retries > 10) {
          throw new Error('Timeout trying to login into concourse')
        }
        sleep.sleep(3)
        retries += 1
      }
    }

    console.log('syncing')
    const sync = spawn('fly', [
      'sync',
      '-t', 'bakery-cli'
    ], { stdio: 'inherit' })
    children.push(sync)
    await completion(sync)

    console.log('executing')
    const execute = spawn('fly', [
      'execute',
      '-t', 'bakery-cli',
      ...cmdArgs
    ], {
      stdio: 'inherit',
      env: {
        ...process.env,
        COLUMNS: process.stdout.columns
      }
    })
    children.push(execute)
    await completion(execute)
  } catch (err) {
    if (err.stdout != null) {
      console.log(err.stdout.toString())
    } else {
      console.log(err)
    }
  } finally {
    console.log('cleaning up')
    const cleanUp = spawn('docker-compose', [
      '-f', tmpComposeYml.name,
      'stop'
    ], { stdio: 'inherit' })
    children.push(cleanUp)
    await completion(cleanUp)
  }
}

const yargs = require('yargs')
  .command((() => {
    const commandUsage = 'fetch <server> <collid> <version>'
    const handler = async argv => {
      const buildExec = path.resolve(argv.cops, 'bakery/build')

      const taskContent = execFileSync(buildExec, ['task', 'fetch-book'])
      const tmpTaskFile = tmp.fileSync()
      fs.writeFileSync(tmpTaskFile.name, taskContent)

      const tmpBookDir = tmp.dirSync()
      fs.writeFileSync(path.resolve(tmpBookDir.name, 'server'), argv.server)
      fs.writeFileSync(path.resolve(tmpBookDir.name, 'collection_id'), argv.collid)
      fs.writeFileSync(path.resolve(tmpBookDir.name, 'version'), argv.version)

      const dataDir = path.resolve(argv.data, argv.collid)

      flyExecute([
        '-c', tmpTaskFile.name,
        `--input=book=${tmpBookDir.name}`,
        output(dataDir, 'fetched-book')
      ])
    }
    return {
      command: commandUsage,
      aliases: 'f',
      describe: 'fetch a book',
      builder: yargs => {
        yargs.usage(`Usage: ${process.env.CALLER || 'execute.js'} ${commandUsage}`)
        yargs.positional('server', {
          describe: 'content server to fetch from',
          type: 'string'
        }).positional('collid', {
          describe: 'collection id of collection to fetch',
          type: 'string'
        }).positional('version', {
          describe: 'version of collection to fetch',
          type: 'string'
        })
      },
      handler: argv => {
        handler(argv).catch((err) => { console.error(err) })
      }
    }
  }).call())
  .command((() => {
    const commandUsage = 'assemble <collid>'
    const handler = async argv => {
      const buildExec = path.resolve(argv.cops, 'bakery/build')

      const taskContent = execFileSync(buildExec, ['task', 'assemble-book'])
      const tmpTaskFile = tmp.fileSync()
      fs.writeFileSync(tmpTaskFile.name, taskContent)

      const tmpBookDir = tmp.dirSync()
      fs.writeFileSync(path.resolve(tmpBookDir.name, 'collection_id'), argv.collid)

      const dataDir = path.resolve(argv.data, argv.collid)

      flyExecute([
        '-c', tmpTaskFile.name,
        `--input=book=${tmpBookDir.name}`,
        input(dataDir, 'fetched-book'),
        output(dataDir, 'assembled-book')
      ])
    }
    return {
      command: commandUsage,
      aliases: 'a',
      describe: 'assemble a book',
      builder: yargs => {
        yargs.usage(`Usage: ${process.env.CALLER || 'execute.js'} ${commandUsage}`)
        yargs.positional('collid', {
          describe: 'collection id of collection to work on',
          type: 'string'
        })
      },
      handler: argv => {
        handler(argv).catch((err) => { console.error(err) })
      }
    }
  }).call())
  .command((() => {
    const commandUsage = 'bake <collid> <recipefile> <stylefile>'
    const handler = async argv => {
      const buildExec = path.resolve(argv.cops, 'bakery/build')

      const taskContent = execFileSync(buildExec, ['task', 'bake-book'])
      const tmpTaskFile = tmp.fileSync()
      fs.writeFileSync(tmpTaskFile.name, taskContent)

      const styleName = 'stylesheet'
      const tmpBookDir = tmp.dirSync()
      fs.writeFileSync(path.resolve(tmpBookDir.name, 'collection_id'), argv.collid)
      fs.writeFileSync(path.resolve(tmpBookDir.name, 'style'), styleName)

      const tmpRecipesDir = tmp.dirSync()
      fs.mkdirSync(path.resolve(tmpRecipesDir.name, 'recipes/output/'), { recursive: true })
      fs.mkdirSync(path.resolve(tmpRecipesDir.name, 'styles/output/'), { recursive: true })
      fs.copyFileSync(path.resolve(argv.recipefile), path.resolve(tmpRecipesDir.name, `recipes/output/${styleName}.css`))
      fs.copyFileSync(path.resolve(argv.stylefile), path.resolve(tmpRecipesDir.name, `styles/output/${styleName}-pdf.css`))

      const dataDir = path.resolve(argv.data, argv.collid)

      flyExecute([
        '-c', tmpTaskFile.name,
        `--input=book=${tmpBookDir.name}`,
        input(dataDir, 'assembled-book'),
        `--input=cnx-recipes=${tmpRecipesDir.name}`,
        output(dataDir, 'baked-book')
      ])
    }
    return {
      command: commandUsage,
      aliases: 'b',
      describe: 'bake a book',
      builder: yargs => {
        yargs.usage(`Usage: ${process.env.CALLER || 'execute.js'} ${commandUsage}`)
        yargs.positional('collid', {
          describe: 'collection id of collection to work on',
          type: 'string'
        }).positional('recipefile', {
          describe: 'path to recipe file',
          type: 'string'
        }).positional('stylefile', {
          describe: 'path to style file',
          type: 'string'
        })
      },
      handler: argv => {
        handler(argv).catch((err) => { console.error(err) })
      }
    }
  }).call())
  .command((() => {
    const commandUsage = 'mathify <collid>'
    const handler = async argv => {
      const buildExec = path.resolve(argv.cops, 'bakery/build')

      const taskContent = execFileSync(buildExec, ['task', 'mathify-book'])
      const tmpTaskFile = tmp.fileSync()
      fs.writeFileSync(tmpTaskFile.name, taskContent)

      const tmpBookDir = tmp.dirSync()
      fs.writeFileSync(path.resolve(tmpBookDir.name, 'collection_id'), argv.collid)

      const dataDir = path.resolve(argv.data, argv.collid)

      flyExecute([
        '-c', tmpTaskFile.name,
        `--input=book=${tmpBookDir.name}`,
        input(dataDir, 'baked-book'),
        output(dataDir, 'mathified-book')
      ])
    }
    return {
      command: commandUsage,
      aliases: 'm',
      describe: 'mathify a book',
      builder: yargs => {
        yargs.usage(`Usage: ${process.env.CALLER || 'execute.js'} ${commandUsage}`)
        yargs.positional('collid', {
          describe: 'collection id of collection to work on',
          type: 'string'
        })
      },
      handler: argv => {
        handler(argv).catch((err) => { console.error(err) })
      }
    }
  }).call())
  .command((() => {
    const commandUsage = 'build-pdf <collid>'
    const handler = async argv => {
      const buildExec = path.resolve(argv.cops, 'bakery/build')

      const taskContent = execFileSync(buildExec, ['task', 'build-pdf', '-a', '{bucketName: none}'])
      const tmpTaskFile = tmp.fileSync()
      fs.writeFileSync(tmpTaskFile.name, taskContent)

      const tmpBookDir = tmp.dirSync()
      fs.writeFileSync(path.resolve(tmpBookDir.name, 'collection_id'), argv.collid)
      fs.writeFileSync(path.resolve(tmpBookDir.name, 'pdf_filename'), 'collection.pdf')

      const dataDir = path.resolve(argv.data, argv.collid)

      flyExecute([
        '-c', tmpTaskFile.name,
        `--input=book=${tmpBookDir.name}`,
        input(dataDir, 'mathified-book'),
        output(dataDir, 'artifacts')
      ])
    }
    return {
      command: commandUsage,
      aliases: 'p',
      describe: 'build a pdf from a book',
      builder: yargs => {
        yargs.usage(`Usage: ${process.env.CALLER || 'execute.js'} ${commandUsage}`)
        yargs.positional('collid', {
          describe: 'collection id of collection to work on',
          type: 'string'
        })
      },
      handler: argv => {
        handler(argv).catch((err) => { console.error(err) })
      }
    }
  }).call())
  .command((() => {
    const commandUsage = 'assemble-meta <collid>'
    const handler = async argv => {
      const buildExec = path.resolve(argv.cops, 'bakery/build')

      const taskContent = execFileSync(buildExec, ['task', 'assemble-book-metadata'])
      const tmpTaskFile = tmp.fileSync()
      fs.writeFileSync(tmpTaskFile.name, taskContent)

      const dataDir = path.resolve(argv.data, argv.collid)

      flyExecute([
        '-c', tmpTaskFile.name,
        input(dataDir, 'assembled-book'),
        output(dataDir, 'assembled-book-metadata')
      ])
    }
    return {
      command: commandUsage,
      aliases: 'am',
      describe: 'build metadata files from an assembled book',
      builder: yargs => {
        yargs.usage(`Usage: ${process.env.CALLER || 'execute.js'} ${commandUsage}`)
        yargs.positional('collid', {
          describe: 'collection id of collection to work on',
          type: 'string'
        })
      },
      handler: argv => {
        handler(argv).catch((err) => { console.error(err) })
      }
    }
  }).call())
  .command((() => {
    const commandUsage = 'bake-meta <collid>'
    const handler = async argv => {
      const buildExec = path.resolve(argv.cops, 'bakery/build')

      const taskContent = execFileSync(buildExec, ['task', 'bake-book-metadata'])
      const tmpTaskFile = tmp.fileSync()
      fs.writeFileSync(tmpTaskFile.name, taskContent)

      const tmpBookDir = tmp.dirSync()
      fs.writeFileSync(path.resolve(tmpBookDir.name, 'collection_id'), argv.collid)

      const dataDir = path.resolve(argv.data, argv.collid)

      flyExecute([
        '-c', tmpTaskFile.name,
        `--input=book=${tmpBookDir.name}`,
        input(dataDir, 'baked-book'),
        input(dataDir, 'assembled-book-metadata'),
        output(dataDir, 'baked-book-metadata')
      ])
    }
    return {
      command: commandUsage,
      aliases: 'bm',
      describe: 'build metadata files from an baked book',
      builder: yargs => {
        yargs.usage(`Usage: ${process.env.CALLER || 'execute.js'} ${commandUsage}`)
        yargs.positional('collid', {
          describe: 'collection id of collection to work on',
          type: 'string'
        })
      },
      handler: argv => {
        handler(argv).catch((err) => { console.error(err) })
      }
    }
  }).call())
  .command((() => {
    const commandUsage = 'disassemble <collid>'
    const handler = async argv => {
      const buildExec = path.resolve(argv.cops, 'bakery/build')

      const taskContent = execFileSync(buildExec, ['task', 'disassemble-book'])
      const tmpTaskFile = tmp.fileSync()
      fs.writeFileSync(tmpTaskFile.name, taskContent)

      const tmpBookDir = tmp.dirSync()
      fs.writeFileSync(path.resolve(tmpBookDir.name, 'collection_id'), argv.collid)

      const dataDir = path.resolve(argv.data, argv.collid)

      flyExecute([
        '-c', tmpTaskFile.name,
        `--input=book=${tmpBookDir.name}`,
        input(dataDir, 'baked-book'),
        input(dataDir, 'baked-book-metadata'),
        output(dataDir, 'disassembled-book')
      ])
    }
    return {
      command: commandUsage,
      aliases: 'd',
      describe: 'disassemble a baked book',
      builder: yargs => {
        yargs.usage(`Usage: ${process.env.CALLER || 'execute.js'} ${commandUsage}`)
        yargs.positional('collid', {
          describe: 'collection id of collection to work on',
          type: 'string'
        })
      },
      handler: argv => {
        handler(argv).catch((err) => { console.error(err) })
      }
    }
  }).call())
  .command((() => {
    const commandUsage = 'jsonify <collid>'
    const handler = async argv => {
      const buildExec = path.resolve(argv.cops, 'bakery/build')

      const taskContent = execFileSync(buildExec, ['task', 'jsonify-book'])
      const tmpTaskFile = tmp.fileSync()
      fs.writeFileSync(tmpTaskFile.name, taskContent)

      const tmpBookDir = tmp.dirSync()
      fs.writeFileSync(path.resolve(tmpBookDir.name, 'collection_id'), argv.collid)

      const dataDir = path.resolve(argv.data, argv.collid)

      flyExecute([
        '-c', tmpTaskFile.name,
        input(dataDir, 'disassembled-book'),
        output(dataDir, 'jsonified-book')
      ])
    }
    return {
      command: commandUsage,
      aliases: 'j',
      describe: 'build metadata from disassembled book',
      builder: yargs => {
        yargs.usage(`Usage: ${process.env.CALLER || 'execute.js'} ${commandUsage}`)
        yargs.positional('collid', {
          describe: 'collection id of collection to work on',
          type: 'string'
        })
      },
      handler: argv => {
        handler(argv).catch((err) => { console.error(err) })
      }
    }
  }).call())
  .option('c', {
    alias: 'cops',
    demandOption: true,
    describe: 'path to output-producer-service directory',
    normalize: true,
    type: 'string'
  })
  .option('d', {
    alias: 'data',
    demandOption: true,
    describe: 'path to data directory',
    normalize: true,
    type: 'string'
  })
  .demandCommand(1, 'command required')
  .help()
  .wrap(process.env.COLUMNS)
  .version(false)
  .strict()
  .fail((msg, err, yargs) => {
    if (err) throw err
    console.error(yargs.help())
    console.error(`\nError: ${msg}`)
    process.exit(1)
  })

yargs.argv // eslint-disable-line
