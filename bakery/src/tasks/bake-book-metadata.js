const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const imageDefault = {
    name: 'openstax/cops-bakery-scripts'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })

  return {
    task: 'bake book metadata',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      inputs: [
        { name: 'book' },
        { name: 'baked-book' },
        { name: 'assembled-book-metadata' }
      ],
      outputs: [{ name: 'baked-book-metadata' }],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee baked-book-metadata/stderr >&2)
          collection_id="$(cat book/collection_id)"
          book_dir="baked-book/$collection_id"
          target_dir="baked-book-metadata/$collection_id"
          mkdir "$target_dir"
          cp "$book_dir/collection.baked.xhtml" "$target_dir/collection.baked.xhtml"
          cp "assembled-book-metadata/$collection_id/collection.assembled-metadata.json" "$target_dir/collection.assembled-metadata.json"
          cd "$target_dir"
          python /code/scripts/bake-book-metadata.py collection.assembled-metadata.json collection.baked.xhtml collection.baked-metadata.json "$collection_id"
          `
        ]
      }
    }
  }
}

module.exports = task
