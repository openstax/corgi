const fs = require('fs')
const path = require('path')
const yaml = require('js-yaml')

const pipelineDir = path.resolve(__dirname, './pipelines')
const envDir = path.resolve(__dirname, '../env')
const commandUsage = 'pipeline <pipelinetype> <env> [options]...'

module.exports.command = commandUsage
module.exports.aliases = ['p']
module.exports.describe = 'builds a pipeline runnable with fly command'
module.exports.builder = yargs => {
  yargs.usage(`Usage: ${process.env.CALLER || 'build.js'} ${commandUsage}`)
  yargs.positional('pipelinetype', {
    describe: 'type of pipeline',
    choices: fs.readdirSync(pipelineDir).map(file => path.basename(file, '.js')),
    type: 'string'
  }).positional('env', {
    describe: 'name of environment',
    choices: fs.readdirSync(envDir).map(file => path.basename(file, '.json')),
    type: 'string'
  }).option('output', {
    alias: ['o'],
    describe: 'path to output file',
    defaultDescription: 'stdout',
    normalize: true,
    requiresArg: true,
    type: 'string'
  }).option('tag', {
    alias: ['t'],
    describe: 'pin pipeline image resources to a tag in the config',
    type: 'string'
  })
}
module.exports.handler = argv => {
  const env = (() => {
    const envFilePath = path.resolve(envDir, `${argv.env}.json`)
    const envFileVals = (() => {
      try {
        return require(envFilePath)
      } catch {
        throw new Error(`Could not find environment file: ${envFilePath}`)
      }
    })()
    // Grab AWS credentials from environment when running locally. If not
    // available, throw an explicit error for the user
    if (envFileVals.ENV_NAME === 'local') {
      envFileVals.S3_ACCESS_KEY_ID = process.env.AWS_ACCESS_KEY_ID
      envFileVals.S3_SECRET_ACCESS_KEY = process.env.AWS_SECRET_ACCESS_KEY
      if (envFileVals.S3_ACCESS_KEY_ID === undefined) {
        throw new Error('Please set AWS_ACCESS_KEY_ID in your environment')
      }
      if (envFileVals.S3_SECRET_ACCESS_KEY === undefined) {
        throw new Error('Please set AWS_SECRET_ACCESS_KEY in your environment')
      }
    }

    return envFileVals
  }).call()
  const pipeline = (() => {
    const pipelineFilePath = path.resolve(pipelineDir, `${argv.pipelinetype}.js`)
    try {
      return require(pipelineFilePath)
    } catch {
      throw new Error(`Could not find pipeline file: ${pipelineFilePath}`)
    }
  }).call()
  const outputFile = argv.output == null
    ? undefined
    : path.resolve(argv.output)

  const pipelineArgs = argv.tag != null ? { ...env, ...{ IMAGE_TAG: argv.tag } } : env
  const pipelineConfig = pipeline(pipelineArgs).config

  const forward = fs.readFileSync(path.resolve(__dirname, 'forward.yml'), { encoding: 'utf8' })
  const output = forward + yaml.safeDump(pipelineConfig)

  if (outputFile) {
    fs.writeFileSync(outputFile, output)
  } else {
    console.log(output)
  }
}