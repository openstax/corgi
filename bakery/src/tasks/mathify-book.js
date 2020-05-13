const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const imageDefault = {
    name: 'openstax/mathify'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })

  return {
    task: 'mathify book',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      inputs: [
        { name: 'book' },
        { name: 'baked-book' }
      ],
      outputs: [{ name: 'mathified-book' }],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee mathified-book/stderr >&2)
          cp -r baked-book/* mathified-book
          book_dir=mathified-book/$(cat book/collection_id)
          node /src/typeset/start -i "$book_dir/collection.baked.xhtml" -o "$book_dir/collection.mathified.xhtml" -f svg  
        `
        ]
      }
    }
  }
}

module.exports = task
