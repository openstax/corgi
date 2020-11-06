const { constructImageSource } = require('../task-util/task-util')

const fs = require('fs')
const path = require('path')

const task = (taskArgs) => {
  const imageDefault = {
    name: 'openstax/mathify',
    tag: 'trunk'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })

  const bookInput = 'book'
  const symlinkInput = 'module-symlinks'
  const linkedInput = 'linked-single'
  const styleInput = 'group-style'
  const mathifiedOutput = 'mathified-single'
  const shellScript = fs.readFileSync(path.resolve(__dirname, '../scripts/mathify_single.sh'), { encoding: "utf-8" })

  return {
    task: 'mathify book',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      inputs: [
        { name: bookInput },
        { name: symlinkInput },
        { name: styleInput },
        { name: linkedInput }
      ],
      outputs: [{ name: mathifiedOutput }],
      params: {
        MATHIFIED_OUTPUT: mathifiedOutput,
        BOOK_INPUT: bookInput,
        SYMLINK_INPUT: symlinkInput,
        STYLE_INPUT: styleInput,
        LINKED_INPUT: linkedInput
      },
      run: {
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
