const dedent = require('dedent')

const task = () => {
  return {
    task: 'jsonify book',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: {
          repository: 'openstax/cops-bakery-scripts'
        }
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
