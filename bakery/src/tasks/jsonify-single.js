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
  const disassembledInput = 'disassembled-single'
  const jsonifiedOutput = 'jsonified-single'

  return {
    task: 'jsonify book',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      inputs: [
        { name: bookInput },
        { name: disassembledInput }
      ],
      outputs: [{ name: jsonifiedOutput }],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee jsonified-book/stderr >&2)
          jsonify "${disassembledInput}" "${jsonifiedOutput}"
          jsonschema -i "${jsonifiedOutput}/$(cat ${bookInput}/slug).toc.json" /code/scripts/book-schema.json
          for jsonfile in "${jsonifiedOutput}/"*@*.json; do
            jsonschema -i "$jsonfile" /code/scripts/page-schema.json
          done
        `
        ]
      }
    }
  }
}

module.exports = task
