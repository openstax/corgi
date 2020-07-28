const test = require('ava')
const { spawn } = require('child_process')
const fs = require('fs-extra')
const path = require('path')
const yaml = require('js-yaml')
const dedent = require('dedent')

const completion = subprocess => {
  const error = new Error()
  return new Promise((resolve, reject) => {
    let stdout = ''
    let stderr = ''
    subprocess.stdout.on('data', data => {
      stdout += data.toString()
    })
    subprocess.stderr.on('data', data => {
      stderr += data.toString()
    })
    subprocess.on('exit', code => {
      if (code === 0) {
        resolve({ stdout, stderr })
      } else {
        error.message = `Subprocess failed with code ${code} and captured output: \n${formatSubprocessOutput({ stdout, stderr })}`
        reject(error)
      }
    })
  })
}

const formatSubprocessOutput = (result) => {
  return dedent`
  ###### stdout ######
  ${result.stdout}
  ###### stderr ######
  ${result.stderr}
  `
}

const sourceObjs = (obj) => {
  const sources = []
  if (typeof obj !== 'object') { return sources }
  if (obj instanceof Array) {
    for (const subobj of obj) {
      sources.push(...sourceObjs(subobj))
    }
  }
  if (obj.type != null && obj.type === 'docker-image') {
    sources.push(obj.source)
  } else {
    for (const key of Object.keys(obj)) {
      sources.push(...sourceObjs(obj[key]))
    }
  }
  return sources
}

test('build pipelines', async t => {
  const envs = (await fs.readdir('env')).map(file => path.basename(file, '.json'))
  const pipelines = (await fs.readdir('src/pipelines')).map(file => path.basename(file, '.js'))

  const processes = []
  for (const pipeline of pipelines) {
    for (const env of envs) {
      processes.push(
        completion(spawn('./build', [
          'pipeline',
          pipeline,
          env
        ],
        {
          // Include credentials in environment for local pipelines
          env: env === 'local' ? {
            ...process.env,
            ...{
              AWS_ACCESS_KEY_ID: 'accesskey',
              AWS_SECRET_ACCESS_KEY: 'secret'
            }
          } : process.env
        }
        ))
      )
    }
  }

  await Promise.all(processes)
  t.pass()
})

test('local pipelines error without credentials', async t => {
  const pipelines = (await fs.readdir('src/pipelines')).map(file => path.basename(file, '.js'))

  for (const pipeline of pipelines) {
    const subproc = completion(spawn('./build', [
      'pipeline',
      pipeline,
      'local'
    ]
    ))

    await t.throwsAsync(
      subproc,
      { message: /Please set AWS_ACCESS_KEY_ID in your environment/ }
    )
  }
})

test('default tag is trunk', async t => {
  let pipelineOut = ''
  const buildPipeline = spawn('./build', [
    'pipeline',
    'pdf',
    'prod'
  ])
  buildPipeline.stdout.on('data', (data) => {
    pipelineOut += data.toString()
  })
  const buildPipelineResult = await completion(buildPipeline)

  const obj = yaml.safeLoad(pipelineOut)
  const sources = sourceObjs(obj)
  for (const source of sources) {
    t.is(source.tag, 'trunk', formatSubprocessOutput(buildPipelineResult))
  }
})

test('pin pipeline tasks to versions', async t => {
  const customTag = 'my-custom-tag'
  let pipelineOut = ''
  const buildPipeline = spawn('./build', [
    'pipeline',
    'pdf',
    'prod',
    `--tag=${customTag}`
  ])
  buildPipeline.stdout.on('data', (data) => {
    pipelineOut += data.toString()
  })
  const buildPipelineResult = await completion(buildPipeline)

  const obj = yaml.safeLoad(pipelineOut)
  const sources = sourceObjs(obj)
  for (const source of sources) {
    t.is(source.tag, customTag, formatSubprocessOutput(buildPipelineResult))
  }
})

test('stable flow in pdf and distribution pipeline', async t => {
  // Prepare test data
  const bookId = 'col30149'
  const outputDir = 'src/tests/output'
  const dataDir = 'src/tests/data'
  try {
    await fs.rmdir(outputDir, { recursive: true })
  } catch {}
  await fs.copy(`${dataDir}/${bookId}`, `${outputDir}/${bookId}`)

  const commonArgs = [
    'run',
    `--data=${outputDir}`,
    '--persist'
  ]

  // Build local cops-bakery-scripts image
  const scriptsImageBuild = spawn('docker', [
    'build',
    'src/scripts',
    '--tag=localhost:5000/openstax/cops-bakery-scripts:test'
  ])
  await completion(scriptsImageBuild)

  // Log a heartbeat every minute so CI doesn't timeout
  setInterval(() => {
    console.log('HEARTBEAT\n   /\\ \n__/  \\  _ \n      \\/')
  }, 60000)

  // Start running tasks
  const assemble = spawn('node', [
    'src/cli/execute.js',
    ...commonArgs,
    'assemble',
    bookId
  ])
  const assembleResult = await completion(assemble)
  t.truthy(fs.existsSync(`${outputDir}/${bookId}/assembled-book/${bookId}/collection.assembled.xhtml`), formatSubprocessOutput(assembleResult))

  const assembleValidateXhtml = spawn('node', [
    'src/cli/execute.js',
    ...commonArgs,
    'validate-xhtml',
    bookId,
    'assembled-book',
    'collection.assembled.xhtml'
  ])
  await completion(assembleValidateXhtml)

  const assembleMeta = spawn('node', [
    'src/cli/execute.js',
    ...commonArgs,
    '--image=localhost:5000/openstax/cops-bakery-scripts:test',
    'assemble-meta',
    bookId
  ])
  const assembleMetaResult = await completion(assembleMeta)
  t.truthy(fs.existsSync(`${outputDir}/${bookId}/assembled-book-metadata/${bookId}/collection.assembled-metadata.json`), formatSubprocessOutput(assembleMetaResult))

  const bake = spawn('node', [
    'src/cli/execute.js',
    ...commonArgs,
    'bake',
    bookId,
    `${dataDir}/col30149-recipe.css`,
    `${dataDir}/blank-style.css`
  ])
  const bakeResult = await completion(bake)
  t.truthy(fs.existsSync(`${outputDir}/${bookId}/baked-book/${bookId}/collection.baked.xhtml`), formatSubprocessOutput(bakeResult))

  const bakeValidateXhtml = spawn('node', [
    'src/cli/execute.js',
    ...commonArgs,
    'validate-xhtml',
    bookId,
    'baked-book',
    'collection.baked.xhtml'
  ])
  await completion(bakeValidateXhtml)

  // PDF
  const mathify = spawn('node', [
    'src/cli/execute.js',
    ...commonArgs,
    'mathify',
    bookId
  ])

  // Distribution
  const checksum = spawn('node', [
    'src/cli/execute.js',
    ...commonArgs,
    '--image=localhost:5000/openstax/cops-bakery-scripts:test',
    'checksum',
    bookId
  ])

  // PDF continued
  const branchPdf = completion(mathify).then(async (mathifyResult) => {
    // mathify assertion
    t.truthy(fs.existsSync(`${outputDir}/${bookId}/mathified-book/${bookId}/collection.mathified.xhtml`), formatSubprocessOutput(mathifyResult))

    const mathifyValidateXhtml = spawn('node', [
      'src/cli/execute.js',
      ...commonArgs,
      'validate-xhtml',
      bookId,
      'mathified-book',
      'collection.mathified.xhtml'
    ])
    await completion(mathifyValidateXhtml)

    const buildPdf = spawn('node', [
      'src/cli/execute.js',
      ...commonArgs,
      'build-pdf',
      bookId
    ])
    const buildPdfResult = await completion(buildPdf)
    t.truthy(fs.existsSync(`${outputDir}/${bookId}/artifacts/collection.pdf`), formatSubprocessOutput(buildPdfResult))
    t.is(fs.readFileSync(`${outputDir}/${bookId}/artifacts/pdf_url`, { encoding: 'utf8' }), 'https://none.s3.amazonaws.com/collection.pdf', formatSubprocessOutput(buildPdfResult))
  })

  // Distribution continued
  const branchDistribution = completion(checksum).then(async (checksumResult) => {
    // checksum assertion
    t.truthy(fs.existsSync(`${outputDir}/${bookId}/checksum-book/${bookId}/resources`), formatSubprocessOutput(checksumResult))

    const checksumValidateXhtml = spawn('node', [
      'src/cli/execute.js',
      ...commonArgs,
      'validate-xhtml',
      bookId,
      'checksum-book',
      'collection.baked.xhtml'
    ])
    await completion(checksumValidateXhtml)

    const bakeMeta = spawn('node', [
      'src/cli/execute.js',
      ...commonArgs,
      '--image=localhost:5000/openstax/cops-bakery-scripts:test',
      'bake-meta',
      bookId
    ])
    const bakeMetaResult = await completion(bakeMeta)
    t.truthy(fs.existsSync(`${outputDir}/${bookId}/baked-book-metadata/${bookId}/collection.baked-metadata.json`), formatSubprocessOutput(bakeMetaResult))

    const disassemble = spawn('node', [
      'src/cli/execute.js',
      ...commonArgs,
      '--image=localhost:5000/openstax/cops-bakery-scripts:test',
      'disassemble',
      bookId
    ])
    const disassembleResult = await completion(disassemble)
    t.truthy(fs.existsSync(`${outputDir}/${bookId}/disassembled-book/${bookId}/disassembled/collection.toc.xhtml`), formatSubprocessOutput(disassembleResult))

    const disassembleValidateXhtml = spawn('node', [
      'src/cli/execute.js',
      ...commonArgs,
      'validate-xhtml',
      bookId,
      'disassembled-book',
      'disassembled/*@*.xhtml'
    ])
    await completion(disassembleValidateXhtml)

    const jsonify = spawn('node', [
      'src/cli/execute.js',
      ...commonArgs,
      '--image=localhost:5000/openstax/cops-bakery-scripts:test',
      'jsonify',
      bookId
    ])
    const jsonifyResult = await completion(jsonify)
    t.truthy(fs.existsSync(`${outputDir}/${bookId}/jsonified-book/${bookId}/jsonified/collection.toc.json`), formatSubprocessOutput(jsonifyResult))

    const jsonifyValidateXhtml = spawn('node', [
      'src/cli/execute.js',
      ...commonArgs,
      'validate-xhtml',
      bookId,
      'jsonified-book',
      'jsonified/*@*.xhtml'
    ])
    await completion(jsonifyValidateXhtml)
  })

  await Promise.all([branchPdf, branchDistribution])
  t.pass()
})
