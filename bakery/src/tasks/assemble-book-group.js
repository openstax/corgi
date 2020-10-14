const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const imageDefault = {
    name: 'openstax/nebuchadnezzar',
    tag: 'trunk'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })
  const inputName = 'fetched-book-group'
  const outputName = 'assembled-book-group'
  const rawCollectionDir = `${inputName}/$(cat ../book/slug)/raw`

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
        { name: inputName }
      ],
      outputs: [{ name: outputName }],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee ${outputName}/stderr >&2)
          book_dir="${outputName}/$(cat ../book/slug)"
          for collection in $(find "${rawCollectionDir}/collections/" -type f); do
            mv "$collection" "${rawCollectionDir}/modules/collection.xml"
            neb assemble "${rawCollectionDir}/modules" "$book_dir/$(basename "$collection" | awk -F'[.]' '{ print $1; }')"
          done
        `
        ]
      }
    }
  }
}

module.exports = task
