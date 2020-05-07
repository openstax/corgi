const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = ({ imageRegistry, imageName, imageTag }) => {
  const imageSource = (constructImageSource({ imageRegistry, imageName, imageTag }) ||
    { repository: 'openstax/cops-bakery-scripts' }
  )
  return {
    task: 'disassemble book',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      inputs: [
        { name: 'book' },
        { name: 'fetched-book' },
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
          book_metadata="fetched-book/$collection_id/raw/metadata.json"
          book_uuid="$(cat $book_metadata | jq -r '.id')"
          book_version="$(cat $book_metadata | jq -r '.version')"
          cp -r baked-book/* disassembled-book
          cp "baked-book-metadata/$collection_id/collection.baked-metadata.json" "disassembled-book/$collection_id/collection.baked-metadata.json"
          book_dir="disassembled-book/$collection_id"
          mkdir "$book_dir/disassembled"
          python /code/scripts/disassemble-book.py "$book_dir" "$book_uuid" "$book_version"
        `
        ]
      }
    }
  }
}

module.exports = task
