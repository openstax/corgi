const { constructImageSource } = require('../task-util/task-util')
const fs = require('fs')
const path = require('path')

const task = (taskArgs) => {
  const imageDefault = {
    name: 'openstax/cops-bakery-scripts',
    tag: 'trunk'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })

  const bookInput = 'book'
  const fetchedInput = 'fetched-book-git'
  const bakedInput = 'baked-book-git'
  const assembledMetaInput = 'assembled-book-metadata-git'
  const bakedMetaOutput = 'baked-book-metadata-git'
  const linkedOutput = 'linked-git'
  const shellScript = fs.readFileSync(path.resolve(__dirname, '../scripts/bake_book_metadata_single.sh'), { encoding: 'utf-8' })

  return {
    task: 'bake book metadata single',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      inputs: [
        { name: bookInput },
        { name: fetchedInput },
        { name: bakedInput },
        { name: assembledMetaInput }
      ],
      outputs: [
        { name: bakedMetaOutput },
        { name: linkedOutput }
      ],
      params: {
        BAKED_META_OUTPUT: bakedMetaOutput,
        LINKED_OUTPUT: linkedOutput,
        BAKED_INPUT: bakedInput,
        FETCHED_INPUT: fetchedInput,
        ASSEMBLED_META_INPUT: assembledMetaInput,
        BOOK_INPUT: bookInput
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
