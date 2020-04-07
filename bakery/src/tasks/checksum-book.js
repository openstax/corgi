const dedent = require('dedent')

const task = () => {
  return {
    task: 'checksum book',
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
      outputs: [{ name: 'checksum-book' }],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee checksum-book/stderr >&2)
          collection_id="$(cat book/collection_id)"
          cp -r baked-book/* checksum-book
          book_dir="checksum-book/$collection_id"
          mkdir "$book_dir/baked"
          cp baked-book/* "$book_dir/baked"
          python /code/scripts/checksum-resources.py "$book_dir"
        `
        ]
      }
    }
  }
}

module.exports = task
