const dedent = require('dedent')

const task = () => {
  return {
    task: 'bake book metadata',
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
          mkdir "baked-book-metadata/$collection_id"
          cp "assembled-book-metadata/$collection_id/collection.assembled-metadata.json" "baked-book-metadata/$collection_id/collection.baked-metadata.json"
        `
        ]
      }
    }
  }
}

module.exports = task
