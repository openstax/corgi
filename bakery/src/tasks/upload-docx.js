const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const { parentGoogleFolderId } = taskArgs
  const imageDefault = {
    name: 'openstax/cops-bakery-scripts',
    tag: 'trunk'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })

  return {
    task: 'upload docx',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      params: {
        GOOGLE_SERVICE_ACCOUNT_CREDENTIALS: '((google-service-account-credentials))'
      },
      inputs: [
        { name: 'book' },
        { name: 'docx-book' }
      ],
      run: {
        path: '/bin/bash',
        args: [
          '-ce', // FIXME: Not including -x to avoid displaying credentials when writing to file.
          dedent`
          echo "$GOOGLE_SERVICE_ACCOUNT_CREDENTIALS" > /tmp/service_account_credentials.json
          collection_id="$(cat book/collection_id)"
          docx_dir="docx-book/$collection_id/docx"
          book_metadata="docx-book/$collection_id/raw/metadata.json"
          book_title="$(cat $book_metadata | jq -r '.title')"
          upload-docx "$docx_dir" "$book_title" "${parentGoogleFolderId}" /tmp/service_account_credentials.json
        `
        ]
      }
    }
  }
}

module.exports = task
