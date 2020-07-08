const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const imageDefault = {
    name: 'openstax/cops-bakery-scripts',
    tag: 'master'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })

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
          jsonschema -i "$target_dir/collection.toc.json" /code/scripts/book-schema.json
          for jsonfile in "$target_dir/"*@*.json; do
            jsonschema -i "$jsonfile" /code/scripts/page-schema.json
          done
        `
        ]
      }
    }
  }
}

module.exports = task
