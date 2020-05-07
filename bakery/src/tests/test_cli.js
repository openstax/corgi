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

test('test', async t => {
  const bookId = 'col30149'
  const outputDir = 'src/tests/output'
  try {
    await fs.rmdir(outputDir, { recursive: true })
  } catch {}
  await fs.copy(`src/tests/data/${bookId}`, `${outputDir}/${bookId}`)
  const child = spawn('node', [
    'src/cli/execute.js',
    '-c',
    '..',
    '-d',
    outputDir,
    'assemble',
    bookId
  ], { stdio: 'inherit' })
  await completion(child)
  t.truthy(fs.existsSync(`${outputDir}/${bookId}/assembled-book/${bookId}/collection.assembled.xhtml`))
})
