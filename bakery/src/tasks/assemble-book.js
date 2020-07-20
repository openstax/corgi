const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const imageDefault = {
    name: 'openstax/nebuchadnezzar',
    tag: 'trunk'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })

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
          cp -r fetched-book/* assembled-book
          cd assembled-book
          book_dir="../assembled-book/$(cat ../book/collection_id)"
          neb assemble "$book_dir/raw" "$book_dir"
        `
        ]
      }
    }
  }
}

module.exports = task
