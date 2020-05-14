const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const { awsAccessKeyId, awsSecretAccessKey, bucketName, feedFileUrl } = taskArgs
  const imageDefault = {
    name: 'openstax/cops-bakery-scripts'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })

  return {
    task: 'check feed',
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
      outputs: [{ name: 'book' }],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee book/stderr >&2)
          curl ${feedFileUrl} -o book-feed.json
          feed_ids=$(cat book-feed.json | jq -r '..|.feed_id?')
          echo "$feed_ids" | while read item
          do
            aws s3api head-object --bucket ${bucketName} --key "$item/.complete" || {
              feed_entry=$(cat book-feed.json | jq -r --arg item $item '.[] | select(.feed_id==$item)')
              echo -n "$(echo $feed_entry | jq -r '.collection_id')" >book/collection_id
              echo -n "$(echo $feed_entry | jq -r '.server')" >book/server
              echo -n "$(echo $feed_entry | jq -r '.style')" >book/style
              echo -n "$(echo $feed_entry | jq -r '.version')" >book/version
              break
            }
          done
        `
        ]
      }
    }
  }
}

module.exports = task
