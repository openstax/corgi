const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const imageDefault = {
    name: 'openstax/cops-bakery-scripts'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })

  return {
    task: 'assemble book metadata',
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
      outputs: [{ name: 'assembled-book-metadata' }],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee assembled-book-metadata/stderr >&2)
          collection_id="$(cat book/collection_id)"
          book_dir="assembled-book/$collection_id"
          target_dir="assembled-book-metadata/$collection_id"
          mkdir "$target_dir"
          python /code/scripts/assemble-book-metadata.py "$book_dir" "$target_dir/collection.assembled-metadata.json"
        `
        ]
      }
    }
  }
}

module.exports = task
