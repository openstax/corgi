const test = require('ava')
const { spawn } = require('child_process')
const fs = require('fs-extra')

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

test('stable flow in content distribution pipeline', async t => {
  // Prepare test data
  const bookId = 'col30149'
  const outputDir = 'src/tests/output'
  const dataDir = 'src/tests/data'
  try {
    await fs.rmdir(outputDir, { recursive: true })
  } catch {}
  await fs.copy(`${dataDir}/${bookId}`, `${outputDir}/${bookId}`)

  // Build local cops-bakery-scripts image
  const scriptsImageBuild = spawn('docker', [
    'build',
    'src/scripts',
    '--tag=localhost.localdomain:5000/openstax/cops-bakery-scripts:test'
  ], { stdio: 'inherit' })
  await completion(scriptsImageBuild)

  const assemble = spawn('node', [
    'src/cli/execute.js',
    '--cops=..',
    `--data=${outputDir}`,
    '--persist',
    'assemble',
    bookId
  ], { stdio: 'inherit' })
  await completion(assemble)
  t.truthy(fs.existsSync(`${outputDir}/${bookId}/assembled-book/${bookId}/collection.assembled.xhtml`))

  const assembleMeta = spawn('node', [
    'src/cli/execute.js',
    '--cops=..',
    `--data=${outputDir}`,
    '--image=localhost.localdomain:5000/openstax/cops-bakery-scripts:test',
    '--persist',
    'assemble-meta',
    bookId
  ], { stdio: 'inherit' })
  await completion(assembleMeta)
  t.truthy(fs.existsSync(`${outputDir}/${bookId}/assembled-book-metadata/${bookId}/collection.assembled-metadata.json`))

  const bake = spawn('node', [
    'src/cli/execute.js',
    '--cops=..',
    `--data=${outputDir}`,
    '--persist',
    'bake',
    bookId,
    `${dataDir}/col30149-recipe.css`,
    `${dataDir}/blank-style.css`
  ], { stdio: 'inherit' })
  await completion(bake)
  t.truthy(fs.existsSync(`${outputDir}/${bookId}/baked-book/${bookId}/collection.baked.xhtml`))

  const bakeMeta = spawn('node', [
    'src/cli/execute.js',
    '--cops=..',
    `--data=${outputDir}`,
    '--image=localhost.localdomain:5000/openstax/cops-bakery-scripts:test',
    '--persist',
    'bake-meta',
    bookId
  ], { stdio: 'inherit' })
  await completion(bakeMeta)
  t.truthy(fs.existsSync(`${outputDir}/${bookId}/baked-book-metadata/${bookId}/collection.baked-metadata.json`))

  const disassemble = spawn('node', [
    'src/cli/execute.js',
    '--cops=..',
    `--data=${outputDir}`,
    '--image=localhost.localdomain:5000/openstax/cops-bakery-scripts:test',
    '--persist',
    'disassemble',
    bookId
  ], { stdio: 'inherit' })
  await completion(disassemble)
  t.truthy(fs.existsSync(`${outputDir}/${bookId}/disassembled-book/${bookId}/disassembled/collection.toc.xhtml`))

  const jsonify = spawn('node', [
    'src/cli/execute.js',
    '--cops=..',
    `--data=${outputDir}`,
    '--image=localhost.localdomain:5000/openstax/cops-bakery-scripts:test',
    'jsonify',
    bookId
  ], { stdio: 'inherit' })
  await completion(jsonify)
  t.truthy(fs.existsSync(`${outputDir}/${bookId}/jsonified-book/${bookId}/jsonified/collection.toc.json`))
})
