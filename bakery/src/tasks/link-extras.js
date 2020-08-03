const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const { server } = taskArgs
  const imageDefault = {
    name: 'openstax/cops-bakery-scripts',
    tag: 'trunk'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })

  return {
    task: 'link extras',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      inputs: [
        { name: 'book' },
        { name: 'assembled-book' }
      ],
      outputs: [{ name: 'linked-extras' }],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee linked-extras/stderr >&2)
          cp -r assembled-book/* linked-extras
          cd linked-extras
          book_dir="./$(cat ../book/collection_id)"
          link-extras "$book_dir" ${server} "/code/scripts/canonical-book-list.json"
        `
        ]
      }
    }
  }
}

module.exports = task
