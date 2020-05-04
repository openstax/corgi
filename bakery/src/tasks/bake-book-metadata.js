const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  // By default, use the cops-bakery-scripts image on Docker Hub
  // if details given, find alternative image
  const { imageRegistry, imageName, imageTag } = taskArgs == null ? {} : taskArgs
  const imageSource = (constructImageSource({ imageRegistry, imageName, imageTag }) ||
    { repository: 'openstax/cops-bakery-scripts' }
  )
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
        { name: 'fetched-book' },
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
          book_metadata="fetched-book/$collection_id/raw/metadata.json"
          book_uuid="$(cat $book_metadata | jq -r '.id')"
          book_version="$(cat $book_metadata | jq -r '.version')"
          book_license="$(cat $book_metadata | jq '.license')"
          book_dir="baked-book/$collection_id"
          target_dir="baked-book-metadata/$collection_id"
          mkdir "$target_dir"
          cp "$book_dir/collection.baked.xhtml" "$target_dir/collection.baked.xhtml"
          cat "assembled-book-metadata/$collection_id/collection.assembled-metadata.json" | jq --arg colid "$collection_id" --arg uuid "$book_uuid" --arg version "$book_version" --argjson license "$book_license" \
              '. + {($colid): {id: $uuid, version: $version, license: $license}}' > "$target_dir/collection.metadata.json"
          cd "$target_dir"
          python /code/scripts/bake-book-metadata.py collection.metadata.json collection.baked.xhtml collection.baked-metadata.json "$collection_id"
          `
        ]
      }
    }
  }
}

module.exports = task
