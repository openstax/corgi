const path = require('path')
const fs = require('fs')
const http = require('http')
const { execFileSync, spawn } = require('child_process')
const waitPort = require('wait-port')
const which = require('which')
const tmp = require('tmp')
tmp.setGracefulCleanup()

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms))

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

const stripLocalPrefix = imageArg => {
  return imageArg.replace(/^(localhost:5000)\//, '')
}

const imageDetailsFromArgs = (argv) => {
  let imageDetails = null
  if (argv.image) {
    imageDetails = extractLocalImageDetails(argv.image)
  }
  if (argv.tag) {
    imageDetails = { tag: argv.tag }
  }
  console.log(`extracted image details: ${JSON.stringify(imageDetails)}`)
  return imageDetails == null ? null : { image: imageDetails }
}

const extractLocalImageDetails = imageArg => {
  if (imageArg == null) {
    return null
  }
  const imageArgStripped = stripLocalPrefix(imageArg)
  const tagNameSeparatorIndex = imageArgStripped.lastIndexOf(':')
  let imageName, imageTag
  if (tagNameSeparatorIndex === -1) {
    imageName = imageArgStripped
    imageTag = 'latest'
  } else {
    imageName = imageArgStripped.slice(0, tagNameSeparatorIndex)
    imageTag = imageArgStripped.slice(tagNameSeparatorIndex + 1)
  }
  const details = {
    registry: 'registry:5000',
    name: imageName,
    tag: imageTag
  }
  return details
}

const input = (dataDir, name) => `--input=${name}=${dataDir}/${name}`
const output = (dataDir, name) => `--output=${name}=${dataDir}/${name}`

const composeYml = fs.readFileSync(path.resolve(__dirname, 'docker-compose.yml'), { encoding: 'utf8' })

const flyExecute = async (cmdArgs, { image, persist }) => {
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

  let error
  try {
    if (image != null) {
      console.log('waiting for registry to wake up')
      await waitPort({
        protocol: 'http',
        host: 'localhost',
        port: 5000,
        path: '/v2/_catalog',
        timeout: 30000,
        output: 'silent'
      })
      const imageStripped = stripLocalPrefix(image)
      if (imageStripped === image) {
        throw new Error(`Specified image ${image} does not have prefix 'localhost:5000'. Not safe to automatically push!`)
      }
      console.log(`uploading image: ${image}`)
      const pushImage = spawn('docker', [
        'push',
        image
      ], { stdio: 'inherit' })
      await completion(pushImage)
    }

    console.log('waiting for concourse to wake up')
    await waitPort({
      protocol: 'http',
      host: 'localhost',
      port: 8080,
      path: '/api/v1/info',
      timeout: 90000,
      output: 'silent'
    })

    console.log('syncing fly')
    let flyPath
    try {
      flyPath = which.sync('fly')
    } catch {
      console.log('no fly installation detected on PATH')
      const flyDir = path.resolve(process.env.HOME, '.local/bin/')
      flyPath = path.resolve(flyDir, 'bakery-cli-fly')
      fs.mkdirSync(flyDir, { recursive: true })
    }

    let needsDownload = false
    if (fs.existsSync(flyPath)) {
      console.log(`detected fly cli installation at ${flyPath}`)
      const printOldFlyVersion = spawn(flyPath, ['--version'], { stdio: 'inherit' })
      children.push(printOldFlyVersion)
      await completion(printOldFlyVersion)
      try {
        const sync = spawn(flyPath, [
          'sync',
          '-c', 'http://localhost:8080'
        ], { stdio: 'inherit' })
        children.push(sync)
        await completion(sync)
      } catch (err) {
        needsDownload = true
      }
    } else {
      needsDownload = true
    }

    if (needsDownload) {
      console.log('syncing fly cli via direct download')
      const flyUrl = `http://localhost:8080/api/v1/cli?arch=amd64&platform=${process.platform}`
      const newFly = await new Promise((resolve, reject) => {
        let newFlyData = Buffer.from('')
        http.get(flyUrl, response => {
          const { statusCode } = response
          if (statusCode !== 200) { reject(new Error(`Request failed. Code: ${statusCode}`)) }
          response.on('data', chunk => { newFlyData = Buffer.concat([newFlyData, chunk]) })
          response.on('end', () => { resolve(newFlyData) })
        }).on('error', (err) => { reject(new Error(`Connection error. Code: ${err.code || 'undefined'}`)) })
      })
      fs.writeFileSync(flyPath, newFly)
      fs.chmodSync(flyPath, 0o776)
      const printNewFlyVersion = spawn(flyPath, ['--version'], { stdio: 'inherit' })
      children.push(printNewFlyVersion)
      await completion(printNewFlyVersion)
    }

    console.log('logging in')
    const login = spawn(flyPath, [
      'login',
      '-k',
      '-t', 'bakery-cli',
      '-c', 'http://localhost:8080',
      '-u', 'admin',
      '-p', 'admin'
    ], { stdio: 'inherit' })
    children.push(login)
    await completion(login)

    console.log('waiting for concourse to settle')
    await sleep(5000)

    const flyArgs = [
      'execute',
      '-t', 'bakery-cli',
      '--include-ignored',
      ...cmdArgs
    ]
    console.log(`executing fly with args: ${flyArgs}`)
    const execute = spawn(flyPath, flyArgs, {
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
    error = err
  } finally {
    if (!persist) {
      console.log('cleaning up')
      const cleanUp = spawn('docker-compose', [
        '-f', tmpComposeYml.name,
        'stop'
      ], { stdio: 'inherit' })
      children.push(cleanUp)
      await completion(cleanUp)
    } else {
      console.log('persisting containers')
    }
  }
  if (error != null) {
    throw error
  }
}

const yargs = require('yargs')
  .command((() => {
    const commandUsage = 'fetch <server> <collid> <version>'
    const handler = async argv => {
      const buildExec = path.resolve(argv.cops, 'bakery/build')

      const imageDetails = imageDetailsFromArgs(argv)
      const taskArgs = imageDetails == null
        ? []
        : [`--taskargs=${JSON.stringify(imageDetails)}`]
      const taskContent = execFileSync(buildExec, ['task', 'fetch-book', ...taskArgs])
      const tmpTaskFile = tmp.fileSync()
      fs.writeFileSync(tmpTaskFile.name, taskContent)

      const tmpBookDir = tmp.dirSync()
      fs.writeFileSync(path.resolve(tmpBookDir.name, 'server'), argv.server)
      fs.writeFileSync(path.resolve(tmpBookDir.name, 'collection_id'), argv.collid)
      fs.writeFileSync(path.resolve(tmpBookDir.name, 'version'), argv.version)

      const dataDir = path.resolve(argv.data, argv.collid)

      await flyExecute([
        '-c', tmpTaskFile.name,
        `--input=book=${tmpBookDir.name}`,
        output(dataDir, 'fetched-book')
      ], { image: argv.image, persist: argv.persist })
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
        handler(argv).catch((err) => { console.error(err); process.exit(1) })
      }
    }
  }).call())
  .command((() => {
    const commandUsage = 'assemble <collid>'
    const handler = async argv => {
      const buildExec = path.resolve(argv.cops, 'bakery/build')

      const imageDetails = imageDetailsFromArgs(argv)
      const taskArgs = imageDetails == null
        ? []
        : [`--taskargs=${JSON.stringify(imageDetails)}`]
      const taskContent = execFileSync(buildExec, ['task', 'assemble-book', ...taskArgs])
      const tmpTaskFile = tmp.fileSync()
      fs.writeFileSync(tmpTaskFile.name, taskContent)

      const tmpBookDir = tmp.dirSync()
      fs.writeFileSync(path.resolve(tmpBookDir.name, 'collection_id'), argv.collid)

      const dataDir = path.resolve(argv.data, argv.collid)

      await flyExecute([
        '-c', tmpTaskFile.name,
        `--input=book=${tmpBookDir.name}`,
        input(dataDir, 'fetched-book'),
        output(dataDir, 'assembled-book')
      ], { image: argv.image, persist: argv.persist })
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
        handler(argv).catch((err) => { console.error(err); process.exit(1) })
      }
    }
  }).call())
  .command((() => {
    const commandUsage = 'bake <collid> <recipefile> <stylefile>'
    const handler = async argv => {
      const buildExec = path.resolve(argv.cops, 'bakery/build')

      const imageDetails = imageDetailsFromArgs(argv)
      const taskArgs = imageDetails == null
        ? []
        : [`--taskargs=${JSON.stringify(imageDetails)}`]
      const taskContent = execFileSync(buildExec, ['task', 'bake-book', ...taskArgs])
      const tmpTaskFile = tmp.fileSync()
      fs.writeFileSync(tmpTaskFile.name, taskContent)

      const styleName = 'stylesheet'
      const tmpBookDir = tmp.dirSync()
      fs.writeFileSync(path.resolve(tmpBookDir.name, 'collection_id'), argv.collid)
      fs.writeFileSync(path.resolve(tmpBookDir.name, 'style'), styleName)

      const tmpRecipesDir = tmp.dirSync()
      fs.mkdirSync(path.resolve(tmpRecipesDir.name, 'rootfs/recipes/'), { recursive: true })
      fs.mkdirSync(path.resolve(tmpRecipesDir.name, 'rootfs/styles/'), { recursive: true })
      fs.copyFileSync(path.resolve(argv.recipefile), path.resolve(tmpRecipesDir.name, `rootfs/recipes/${styleName}.css`))
      fs.copyFileSync(path.resolve(argv.stylefile), path.resolve(tmpRecipesDir.name, `rootfs/styles/${styleName}-pdf.css`))

      const dataDir = path.resolve(argv.data, argv.collid)

      await flyExecute([
        '-c', tmpTaskFile.name,
        `--input=book=${tmpBookDir.name}`,
        input(dataDir, 'assembled-book'),
        `--input=cnx-recipes-output=${tmpRecipesDir.name}`,
        output(dataDir, 'baked-book')
      ], { image: argv.image, persist: argv.persist })
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
        handler(argv).catch((err) => { console.error(err); process.exit(1) })
      }
    }
  }).call())
  .command((() => {
    const commandUsage = 'mathify <collid>'
    const handler = async argv => {
      const buildExec = path.resolve(argv.cops, 'bakery/build')

      const imageDetails = imageDetailsFromArgs(argv)
      const taskArgs = imageDetails == null
        ? []
        : [`--taskargs=${JSON.stringify(imageDetails)}`]
      const taskContent = execFileSync(buildExec, ['task', 'mathify-book', ...taskArgs])
      const tmpTaskFile = tmp.fileSync()
      fs.writeFileSync(tmpTaskFile.name, taskContent)

      const tmpBookDir = tmp.dirSync()
      fs.writeFileSync(path.resolve(tmpBookDir.name, 'collection_id'), argv.collid)

      const dataDir = path.resolve(argv.data, argv.collid)

      await flyExecute([
        '-c', tmpTaskFile.name,
        `--input=book=${tmpBookDir.name}`,
        input(dataDir, 'baked-book'),
        output(dataDir, 'mathified-book')
      ], { image: argv.image, persist: argv.persist })
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
        handler(argv).catch((err) => { console.error(err); process.exit(1) })
      }
    }
  }).call())
  .command((() => {
    const commandUsage = 'build-pdf <collid>'
    const handler = async argv => {
      const buildExec = path.resolve(argv.cops, 'bakery/build')

      const imageDetails = imageDetailsFromArgs(argv) || {}
      const taskArgs = [`--taskargs=${JSON.stringify({ ...imageDetails, ...{ bucketName: 'none' } })}`]
      const taskContent = execFileSync(buildExec, ['task', 'build-pdf', ...taskArgs])
      const tmpTaskFile = tmp.fileSync()
      fs.writeFileSync(tmpTaskFile.name, taskContent)

      const tmpBookDir = tmp.dirSync()
      fs.writeFileSync(path.resolve(tmpBookDir.name, 'collection_id'), argv.collid)
      fs.writeFileSync(path.resolve(tmpBookDir.name, 'pdf_filename'), 'collection.pdf')

      const dataDir = path.resolve(argv.data, argv.collid)

      await flyExecute([
        '-c', tmpTaskFile.name,
        `--input=book=${tmpBookDir.name}`,
        input(dataDir, 'mathified-book'),
        output(dataDir, 'artifacts')
      ], { image: argv.image, persist: argv.persist })
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
        handler(argv).catch((err) => { console.error(err); process.exit(1) })
      }
    }
  }).call())
  .command((() => {
    const commandUsage = 'assemble-meta <collid>'
    const handler = async argv => {
      const buildExec = path.resolve(argv.cops, 'bakery/build')

      const imageDetails = imageDetailsFromArgs(argv)
      const taskArgs = imageDetails == null
        ? []
        : [`--taskargs=${JSON.stringify(imageDetails)}`]
      const taskContent = execFileSync(buildExec, ['task', 'assemble-book-metadata', ...taskArgs])
      const tmpTaskFile = tmp.fileSync()
      fs.writeFileSync(tmpTaskFile.name, taskContent)

      const tmpBookDir = tmp.dirSync()
      fs.writeFileSync(path.resolve(tmpBookDir.name, 'collection_id'), argv.collid)

      const dataDir = path.resolve(argv.data, argv.collid)

      await flyExecute([
        '-c', tmpTaskFile.name,
        `--input=book=${tmpBookDir.name}`,
        input(dataDir, 'assembled-book'),
        output(dataDir, 'assembled-book-metadata')
      ], { image: argv.image, persist: argv.persist })
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
        handler(argv).catch((err) => { console.error(err); process.exit(1) })
      }
    }
  }).call())
  .command((() => {
    const commandUsage = 'bake-meta <collid>'
    const handler = async argv => {
      const buildExec = path.resolve(argv.cops, 'bakery/build')

      const imageDetails = imageDetailsFromArgs(argv)
      const taskArgs = imageDetails == null
        ? []
        : [`--taskargs=${JSON.stringify(imageDetails)}`]
      const taskContent = execFileSync(buildExec, ['task', 'bake-book-metadata', ...taskArgs])
      const tmpTaskFile = tmp.fileSync()
      fs.writeFileSync(tmpTaskFile.name, taskContent)

      const tmpBookDir = tmp.dirSync()
      fs.writeFileSync(path.resolve(tmpBookDir.name, 'collection_id'), argv.collid)

      const dataDir = path.resolve(argv.data, argv.collid)

      await flyExecute([
        '-c', tmpTaskFile.name,
        `--input=book=${tmpBookDir.name}`,
        input(dataDir, 'fetched-book'),
        input(dataDir, 'baked-book'),
        input(dataDir, 'assembled-book-metadata'),
        output(dataDir, 'baked-book-metadata')
      ], { image: argv.image, persist: argv.persist })
    }
    return {
      command: commandUsage,
      aliases: 'bm',
      describe: 'build metadata files from a baked book',
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
    // fly -t cops-dev execute -c checksum-book.yml -j bakery/bakery -i book=./data/book -i baked-book=./data/baked-book -o checksum-book=./data/checksum-book
    const commandUsage = 'checksum <collid>'
    const handler = async argv => {
      const buildExec = path.resolve(argv.cops, 'bakery/build')

      const imageDetails = imageDetailsFromArgs(argv)
      const taskArgs = imageDetails == null
        ? []
        : [`--taskargs=${JSON.stringify(imageDetails)}`]
      const taskContent = execFileSync(buildExec, ['task', 'checksum-book', ...taskArgs])
      const tmpTaskFile = tmp.fileSync()
      fs.writeFileSync(tmpTaskFile.name, taskContent)

      const tmpBookDir = tmp.dirSync()
      fs.writeFileSync(path.resolve(tmpBookDir.name, 'collection_id'), argv.collid)

      const dataDir = path.resolve(argv.data, argv.collid)

      await flyExecute([
        '-c', tmpTaskFile.name,
        `--input=book=${tmpBookDir.name}`,
        input(dataDir, 'baked-book'),
        output(dataDir, 'checksum-book')
      ], { image: argv.image, persist: argv.persist })
    }
    return {
      command: commandUsage,
      aliases: 'cb',
      describe: 'checksum resources from a baked book',
      builder: yargs => {
        yargs.usage(`Usage: ${process.env.CALLER || 'execute.js'} ${commandUsage}`)
        yargs.positional('collid', {
          describe: 'collection id of collection to work on',
          type: 'string'
        })
      },
      handler: argv => {
        handler(argv).catch((err) => { console.error(err); process.exit(1) })
      }
    }
  }).call())
  .command((() => {
    const commandUsage = 'disassemble <collid>'
    const handler = async argv => {
      const buildExec = path.resolve(argv.cops, 'bakery/build')

      const imageDetails = imageDetailsFromArgs(argv)
      const taskArgs = imageDetails == null
        ? []
        : [`--taskargs=${JSON.stringify(imageDetails)}`]
      const taskContent = execFileSync(buildExec, ['task', 'disassemble-book', ...taskArgs])
      const tmpTaskFile = tmp.fileSync()
      fs.writeFileSync(tmpTaskFile.name, taskContent)

      const tmpBookDir = tmp.dirSync()
      fs.writeFileSync(path.resolve(tmpBookDir.name, 'collection_id'), argv.collid)

      const dataDir = path.resolve(argv.data, argv.collid)

      await flyExecute([
        '-c', tmpTaskFile.name,
        `--input=book=${tmpBookDir.name}`,
        input(dataDir, 'fetched-book'),
        input(dataDir, 'checksum-book'),
        input(dataDir, 'baked-book-metadata'),
        output(dataDir, 'disassembled-book')
      ], { image: argv.image, persist: argv.persist })
    }
    return {
      command: commandUsage,
      aliases: 'd',
      describe: 'disassemble a checksummed book',
      builder: yargs => {
        yargs.usage(`Usage: ${process.env.CALLER || 'execute.js'} ${commandUsage}`)
        yargs.positional('collid', {
          describe: 'collection id of collection to work on',
          type: 'string'
        })
      },
      handler: argv => {
        handler(argv).catch((err) => { console.error(err); process.exit(1) })
      }
    }
  }).call())
  .command((() => {
    const commandUsage = 'jsonify <collid>'
    const handler = async argv => {
      const buildExec = path.resolve(argv.cops, 'bakery/build')

      const imageDetails = imageDetailsFromArgs(argv)
      const taskArgs = imageDetails == null
        ? []
        : [`--taskargs=${JSON.stringify(imageDetails)}`]
      const taskContent = execFileSync(buildExec, ['task', 'jsonify-book', ...taskArgs])
      const tmpTaskFile = tmp.fileSync()
      fs.writeFileSync(tmpTaskFile.name, taskContent)

      const tmpBookDir = tmp.dirSync()
      fs.writeFileSync(path.resolve(tmpBookDir.name, 'collection_id'), argv.collid)

      const dataDir = path.resolve(argv.data, argv.collid)

      await flyExecute([
        '-c', tmpTaskFile.name,
        `--input=book=${tmpBookDir.name}`,
        input(dataDir, 'disassembled-book'),
        output(dataDir, 'jsonified-book')
      ], { image: argv.image, persist: argv.persist })
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
        handler(argv).catch((err) => { console.error(err); process.exit(1) })
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
  .option('i', {
    alias: 'image',
    describe: 'name of image to use instead of default',
    type: 'string'
  })
  .option('t', {
    alias: 'tag',
    describe: 'use a particular tag of the default remote task image resource',
    type: 'string'
  })
  .option('p', {
    alias: 'persist',
    describe: 'persist containers after running cli command',
    boolean: true,
    default: false
  })
  .conflicts('i', 't')
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
