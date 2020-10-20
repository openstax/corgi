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
  const fetchedInput = 'fetched-book-group'
  const symlinkInput = 'module-symlinks'
  const linkedInput = 'linked-single'
  const resourcesOutput = 'checksum-resources'

  return {
    task: 'checksum book',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      inputs: [
        { name: bookInput },
        { name: fetchedInput },
        { name: symlinkInput },
        { name: linkedInput }
      ],
      outputs: [{ name: resourcesOutput }],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee checksum-book/stderr >&2)

          # Add symlinks to fetched-book-group to be able to find images
          find "${symlinkInput}" -type l | xargs -I{} cp -P {} "${linkedInput}"

          checksum "${linkedInput}" "${resourcesOutput}"
        `
        ]
      }
    }
  }
}

module.exports = task
