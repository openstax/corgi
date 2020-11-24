const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const { codeVersion, cloudfrontUrl, distBucketPath } = taskArgs
  const imageDefault = {
    name: 'openstax/cops-bakery-scripts',
    tag: 'trunk'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })

  const distBucketPrefix = `${distBucketPath}${codeVersion}`

  const rexUrl = 'https://rex-web.herokuapp.com'
  const rexProdUrl = 'https://rex-web-production.herokuapp.com'

  return {
    task: 'generate preview urls',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      inputs: [
        { name: 'book' },
        { name: 'jsonified-book' }
      ],
      outputs: [{ name: 'preview-urls' }],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee preview-urls/stderr >&2)
          collection_id="$(cat book/collection_id)"
          book_dir="jsonified-book/$collection_id/jsonified"

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
            <<< '[]' >> preview-urls/content_urls
        `
        ]
      }
    }
  }
}

module.exports = task
