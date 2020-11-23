const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const { awsAccessKeyId, awsSecretAccessKey, distBucket, queueStateBucket, codeVersion, statePrefix, cloudfrontUrl, distBucketPath, updateQueueState = true } = taskArgs
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

  const rexUrl = 'https://rex-web.herokuapp.com'
  const rexProdUrl = 'https://rex-web-production.herokuapp.com'

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
          aws s3 cp "$book_dir/collection.toc.json" "$toc_s3_link_json"
          aws s3 cp "$book_dir/collection.toc.xhtml" "$toc_s3_link_xhtml"

          rex_archive_param="?archive=${cloudfrontUrl}/${distBucketPrefix}"

          book_slug=$(jq -r '.tree.slug' "$book_dir/collection.toc.json")
          first_page_slug=$(jq -r '.tree.contents[0].slug' "$book_dir/collection.toc.json")
          rex_url=${rexUrl}/books/$book_slug/pages/$first_page_slug$rex_archive_param
          rex_prod_url=${rexProdUrl}/books/$book_slug/pages/$first_page_slug$rex_archive_param

          jq \
            --arg rex_url $rex_url \
            --arg rex_prod_url $rex_prod_url \
            '. + [
              { text: "View - Rex Web", href: $rex_url },
              { text: "View - Rex Web Prod", href: $rex_prod_url }
            ]' \
            <<< '[]' >> upload-book/content_urls

          ${updateQueueState ? `complete_filename=".${statePrefix}.$collection_id@$book_legacy_version.complete"
          date -Iseconds > "/tmp/$complete_filename"
          aws s3 cp "/tmp/$complete_filename" "s3://${queueStateBucket}/${codeVersion}/$complete_filename"` : ''}
        `
        ]
      }
    }
  }
}

module.exports = task
