const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const { awsAccessKeyId, awsSecretAccessKey, queueStateBucket, codeVersion, statePrefix } = taskArgs
  const imageDefault = {
    name: 'openstax/cops-bakery-scripts',
    tag: 'trunk'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })

  return {
    task: 'report book complete',
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
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          collection_id="$(cat book/collection_id)"
          book_legacy_version="$(cat book/version)"
          complete_filename=".${statePrefix}.$collection_id@$book_legacy_version.complete"
          date -Iseconds > "/tmp/$complete_filename"
          aws s3 cp "/tmp/$complete_filename" "s3://${queueStateBucket}/${codeVersion}/$complete_filename"
        `
        ]
      }
    }
  }
}

module.exports = task
