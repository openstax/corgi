const { constructImageSource } = require('../task-util/task-util')
const fs = require('fs')
const path = require('path')

const task = (taskArgs) => {
  const imageDefault = {
    name: 'openstax/cnx-easybake',
    tag: 'trunk'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })

  const bookInput = 'book'
  const assembledInput = 'assembled-book-group'
  const recipeInput = 'cnx-recipes-output'
  const bakedOutput = 'baked-book-group'
  const styleOutput = 'group-style'
  const shellScript = fs.readFileSync(path.resolve(__dirname, '../scripts/bake_book_group.sh'), { encoding: 'utf-8' })

  return {
    task: 'bake book group',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      inputs: [
        { name: bookInput },
        { name: assembledInput },
        { name: recipeInput }
      ],
      outputs: [
        { name: bakedOutput },
        { name: styleOutput }
      ],
      params: {
        BAKED_OUTPUT: bakedOutput,
        BOOK_INPUT: bookInput,
        STYLE_OUTPUT: styleOutput,
        ASSEMBLED_INPUT: assembledInput
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
