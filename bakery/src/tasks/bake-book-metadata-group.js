const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const imageDefault = {
    name: 'openstax/cops-bakery-scripts',
    tag: 'trunk'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })

  const fetchedInput = 'fetched-book-group'
  const bakedInput = 'baked-book-group'
  const assembledMetaInput = 'assembled-book-metadata-group'
  const bakedMetaOutput = 'baked-book-metadata-group'

  return {
    task: 'bake book metadata',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      inputs: [
        { name: fetchedInput },
        { name: bakedInput },
        { name: assembledMetaInput }
      ],
      outputs: [{ name: bakedMetaOutput }],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee ${bakedMetaOutput}/stderr >&2)
          for collection in $(find "${bakedInput}/" -path *.baked.xhtml -type f); do
            slug_name=$(basename "$collection" | awk -F'[.]' '{ print $1; }')

            book_metadata="${fetchedInput}/raw/metadata/$slug_name.metadata.json"
            book_uuid="$(cat $book_metadata | jq -r '.id')"
            book_version="$(cat $book_metadata | jq -r '.version')"
            book_legacy_id="$(cat $book_metadata | jq -r '.legacy_id')"
            book_legacy_version="$(cat $book_metadata | jq -r '.legacy_version')"
            book_ident_hash="$book_uuid@$book_version"
            book_license="$(cat $book_metadata | jq '.license')"
            book_slugs_file="${fetchedInput}/book-slugs.json"
            cat "${assembledMetaInput}/$slug_name.assembled-metadata.json" | \
                jq --arg ident_hash "$book_ident_hash" --arg uuid "$book_uuid" --arg version "$book_version" --argjson license "$book_license" \
                --arg legacy_id "$book_legacy_id" --arg legacy_version "$book_legacy_version" \
                '. + {($ident_hash): {id: $uuid, version: $version, license: $license, legacy_id: $legacy_id, legacy_version: $legacy_version}}' > "/tmp/$slug_name.baked-input-metadata.json"
            bake-meta /tmp/$slug_name.baked-input-metadata.json "${bakedInput}/$slug_name.baked.xhtml" "$book_uuid" "$book_slugs_file" "${bakedMetaOutput}/$slug_name.baked-metadata.json"
          done
          `
        ]
      }
    }
  }
}

module.exports = task
