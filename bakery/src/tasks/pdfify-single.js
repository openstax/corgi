const { constructImageSource } = require('../task-util/task-util')
const fs = require('fs')
const path = require('path')

const task = (taskArgs) => {
  const { bucketName } = taskArgs
  const imageDefault = {
    name: 'openstax/princexml',
    tag: 'trunk'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })

  const bookInput = 'book'
  const fetchedInput = 'fetched-book-git'
  const fetchedResourcesInput = 'fetched-book-git-resources'
  const symlinkInput = 'module-symlinks'
  const styleInput = 'git-style'
  const mathifiedInput = 'mathified-git'
  const artifactsOutput = 'artifacts-git'
  const shellScript = fs.readFileSync(path.resolve(__dirname, '../scripts/pdfify_single.sh'), { encoding: 'utf-8' })

  return {
    task: 'build pdf single',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      inputs: [
        { name: bookInput },
        { name: fetchedInput },
        { name: fetchedResourcesInput },
        { name: styleInput },
        { name: symlinkInput },
        { name: mathifiedInput }
      ],
      outputs: [{ name: artifactsOutput }],
      params: {
        ARTIFACTS_OUTPUT: artifactsOutput,
        SYMLINK_INPUT: symlinkInput,
        MATHIFIED_INPUT: mathifiedInput,
        STYLE_INPUT: styleInput,
        BUCKET_NAME: bucketName,
        BOOK_INPUT: bookInput
      },
      run: {
        user: 'root',
        path: '/bin/bash',
        args: [
          '-cxe',
          shellScript
        ]
      }
    }
  }
}

module.exports = task
