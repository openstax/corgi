const dedent = require('dedent')

const task = () => {
  return {
    task: 'disassemble book',
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
        { name: 'baked-book' },
        { name: 'baked-book-metadata' }
      ],
      outputs: [{ name: 'disassembled-book' }],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee disassembled-book/stderr >&2)
          collection_id="$(cat book/collection_id)"
          cp -r baked-book/* disassembled-book
          cp "baked-book-metadata/$collection_id/collection.baked-metadata.json" "disassembled-book/$collection_id/collection.baked-metadata.json"
          book_dir="disassembled-book/$collection_id"
          mkdir "$book_dir/disassembled"
          python /code/scripts/disassemble-book.py "$book_dir" "$collection_id"
        `
        ]
      }
    }
  }
}

module.exports = task
