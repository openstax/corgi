const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  // By default, use the cops-bakery-scripts image on Docker Hub
  // if details given, find alternative image
  const { imageRegistry, imageName, imageTag } = taskArgs == null ? {} : taskArgs
  const imageSource = (constructImageSource({ imageRegistry, imageName, imageTag }) ||
    { repository: 'openstax/cops-bakery-scripts' }
  )
  return {
    task: 'jsonify book',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      inputs: [
        { name: 'book' },
        { name: 'disassembled-book' }
      ],
      outputs: [{ name: 'jsonified-book' }],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee jsonified-book/stderr >&2)
          cp -r disassembled-book/* jsonified-book
          collection_id="$(cat book/collection_id)"
          book_dir="jsonified-book/$collection_id/disassembled"
          target_dir="jsonified-book/$collection_id/jsonified"
          mkdir "$target_dir"
          python /code/scripts/jsonify-book.py "$book_dir" "$target_dir"
        `
        ]
      }
    }
  }
}

module.exports = task
