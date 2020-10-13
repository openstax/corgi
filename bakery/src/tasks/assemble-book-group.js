const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const imageDefault = {
    name: 'openstax/nebuchadnezzar',
    tag: 'trunk'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })

  const slug = 'precalculus'
  return {
    task: 'assemble book',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      inputs: [
        { name: 'book' },
        { name: 'fetched-book' }
      ],
      outputs: [{ name: 'assembled-book' }],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee assembled-book/stderr >&2)
          book_dir="./assembled-book/$(cat ../book/collection_id)"
          for collection in $(find ./fetched-book/col11667/raw/collections/ -type f); do
            mv collection ./fetched-books/
            echo $collection
          done
          neb assemble "$book_dir/raw" "$book_dir"
        `
        ]
      }
    }
  }
}

module.exports = task
