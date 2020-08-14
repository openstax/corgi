const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const imageDefault = {
    name: 'openstax/cops-bakery-scripts',
    tag: 'trunk'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })

  return {
    task: 'gdocify book',
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
      outputs: [{ name: 'gdocified-book' }],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee gdocified-book/stderr >&2)
          cp -r disassembled-book/* gdocified-book
          collection_id="$(cat book/collection_id)"
          book_dir="gdocified-book/$collection_id/disassembled"
          target_dir="gdocified-book/$collection_id/gdocified"
          mkdir "$target_dir"
          gdocify "$book_dir" "$target_dir"
          cp "$book_dir"/*@*-metadata.json "$target_dir"
        `
        ]
      }
    }
  }
}

module.exports = task
