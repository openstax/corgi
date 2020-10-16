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
  const rawCollectionDir = `${inputName}/raw`

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
          # use 'tmp' not '/tmp' so we dont modify outside cwd
          mkdir -p "tmp/data/"
          for collection in $(find "${rawCollectionDir}/collections/" -type f); do
            slug_name=$(basename "$collection" | awk -F'[.]' '{ print $1; }')
            mv "$collection" "${rawCollectionDir}/modules/collection.xml"
            neb assemble "${rawCollectionDir}/modules" "tmp/data/$slug_name"
            cp "tmp/data/$slug_name/collection.assembled.xhtml" "${outputName}/$slug_name.assembled.xhtml"
          done
          `
        ]
      }
    }
  }
}

module.exports = task
