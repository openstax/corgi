const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const { awsAccessKeyId, awsSecretAccessKey, distBucket, codeVersion, distBucketPath } = taskArgs
  const imageDefault = {
    name: 'openstax/cops-bakery-scripts',
    tag: 'trunk'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })
  if (!distBucketPath.endsWith('/') || distBucketPath.length === 0) {
    throw Error('distBucketPath must represent some directory-like path in s3')
  }
  const distBucketPrefix = `${distBucketPath}${codeVersion}`

  return {
    task: 'upload single',
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
        { name: 'jsonified-single' },
        { name: 'checksum-single' },
        { name: 'fetched-book-group-resources' }
      ],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee upload-single/stderr >&2)
          target_dir="upload-single/contents"
          mkdir -p "$target_dir"
          book_dir="jsonified-single"
          resources_dir="checksum-single/resources"
          book_uuid=$(cat book/uuid)
          book_version=$(cat book/version)
          book_slug=$(cat book/slug)
          for jsonfile in "$book_dir/"*@*.json; do cp "$jsonfile" "$target_dir/$(basename $jsonfile)"; done;
          for xhtmlfile in "$book_dir/"*@*.xhtml; do cp "$xhtmlfile" "$target_dir/$(basename $xhtmlfile)"; done;
          aws s3 cp --recursive "$target_dir" "s3://${distBucket}/${distBucketPrefix}/contents"
          copy-resources-s3 "$resources_dir" "${distBucket}" "${distBucketPrefix}/resources"

          #######################################
          # UPLOAD BOOK LEVEL FILES LAST
          # so that if an error is encountered
          # on prior upload steps, those files
          # will not be found by watchers
          #######################################
          toc_s3_link_json="s3://${distBucket}/${distBucketPrefix}/contents/$book_uuid@$book_version.json"
          toc_s3_link_xhtml="s3://${distBucket}/${distBucketPrefix}/contents/$book_uuid@$book_version.xhtml"
          aws s3 cp "$book_dir/$book_slug.toc.json" "$toc_s3_link_json"
          aws s3 cp "$book_dir/$book_slug.toc.xhtml" "$toc_s3_link_xhtml"
        `
        ]
      }
    }
  }
}

module.exports = task
