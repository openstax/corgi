const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const imageDefault = {
    name: 'openstax/cops-bakery-scripts',
    tag: 'trunk'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })

  const bookInput = 'book'
  const resourceLinkedInput = 'resource-linked-single'
  const bakedBookMetaInput = 'baked-book-metadata-group'
  const disassembledOutput = 'disassembled-single'

  return {
    task: 'disassemble book',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      inputs: [
        { name: bookInput },
        { name: resourceLinkedInput },
        { name: bakedBookMetaInput }
      ],
      outputs: [{ name: disassembledOutput }],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee disassembled-book/stderr >&2)
          slug_name=$(cat ${bookInput}/slug)
          disassemble "${resourceLinkedInput}/$slug_name.resource-linked.xhtml" "${bakedBookMetaInput}/$slug_name.baked-metadata.json" "$slug_name" "${disassembledOutput}"
        `
        ]
      }
    }
  }
}

module.exports = task
