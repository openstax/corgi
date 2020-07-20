const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const { awsAccessKeyId, awsSecretAccessKey, distBucket, queueStateBucket, codeVersion } = taskArgs
  const imageDefault = {
    name: 'openstax/cops-bakery-scripts',
    tag: 'trunk'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })
  const distBucketPrefix = `apps/archive/${codeVersion}`

  return {
    task: 'upload book',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      params: {
        AWS_ACCESS_KEY_ID: `${awsAccessKeyId}`,
        AWS_SECRET_ACCESS_KEY: `${awsSecretAccessKey}`
      },
      inputs: [
        { name: 'book' },
        { name: 'jsonified-book' }
      ],
      outputs: [{ name: 'upload-book' }],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee upload-book/stderr >&2)
          collection_id="$(cat book/collection_id)"
          book_legacy_version="$(cat book/version)"
          book_dir="jsonified-book/$collection_id/jsonified"
          book_metadata="jsonified-book/$collection_id/raw/metadata.json"
          resources_dir="jsonified-book/$collection_id/resources"
          target_dir="upload-book/contents"
          mkdir "$target_dir"
          book_uuid="$(cat $book_metadata | jq -r '.id')"
          book_version="$(cat $book_metadata | jq -r '.version')"
          cp "$book_dir/collection.toc.json" "$target_dir/$book_uuid@$book_version.json"
          cp "$book_dir/collection.toc.xhtml" "$target_dir/$book_uuid@$book_version.xhtml"
          for jsonfile in "$book_dir/"*@*.json; do cp "$jsonfile" "$target_dir/$(basename $jsonfile)"; done;
          for xhtmlfile in "$book_dir/"*@*.xhtml; do cp "$xhtmlfile" "$target_dir/$(basename $xhtmlfile)"; done;
          aws s3 cp --recursive "$target_dir" "s3://${distBucket}/${distBucketPrefix}/contents"
          python /code/scripts/copy-resources-s3.py "$resources_dir" "${distBucket}" "${distBucketPrefix}/resources"
          complete_filename=".$collection_id@$book_legacy_version.complete"
          date -Iseconds > "/tmp/$complete_filename"
          aws s3 cp "/tmp/$complete_filename" "s3://${queueStateBucket}/${codeVersion}/$complete_filename"
        `
        ]
      }
    }
  }
}

module.exports = task
