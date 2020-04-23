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
  yargs.positional('env', {
    describe: 'pipeline environment',
    choices: fs.readdirSync(envDir).map(file => path.basename(file, '.json')),
    type: 'string'
  }).positional('pipelinetype', {	
    describe: 'pipeline type',	
    choices: fs.readdirSync(pipelineDir).map(file => path.basename(file, '.js')),	
    type: 'string'	
  }).option('output', {	
    alias: ['o'],	
    describe: 'path to output file',	
    defaultDescription: 'stdout',	
    normalize: true,	
    requiresArg: true,	
    type: 'string'	
  })
}
module.exports.handler = argv => {
  const env = (() => {
    const envFilePath = path.resolve(envDir, `${argv.env}.json`)
    try {
      return require(envFilePath)
    } catch {
      throw new Error(`Could not find environment file: ${envFilePath}`)
    }
  })()
  const pipeline = ((env) => {
    const pipelineFilePath = path.resolve(pipelineDir, `${argv.pipelinetype}.js`)
    try {
      return require(pipelineFilePath)
    } catch {
      throw new Error(`Could not find pipeline file: ${pipelineFilePath}`)
    }
  })()
  const outputFile = argv.output == null
    ? undefined
    : path.resolve(argv.output)
  const pipelineArgs = argv.pipelineargs == null
    ? {}
    : yaml.safeLoad(argv.pipelineargs)

  const pipelineConfig = pipeline(env).config

  const forward = fs.readFileSync(path.resolve(__dirname, 'forward.yml'), { encoding: 'utf8' })
  const output = forward + yaml.safeDump(pipelineConfig)

  if (outputFile) {
    fs.writeFileSync(outputFile, output)
  } else {
    console.log(output)
  }
}