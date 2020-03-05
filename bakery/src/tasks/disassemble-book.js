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
        { name: 'baked-book' }
      ],
      outputs: [{ name: 'disassembled-book' }],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee disassembled-book/stderr >&2)
          cp -r baked-book/* disassembled-book
          book_dir="disassembled-book/$(cat book/collection_id)"
          mkdir "$book_dir/disassembled"
          python /code/scripts/disassemble-book.py "$book_dir"
        `
        ]
      }
    }
  }
}

module.exports = task
