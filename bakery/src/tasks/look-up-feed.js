const dedent = require('dedent')

const task = () => {
  return {
    task: 'look up feed',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: {
          repository: 'openstax/cops-bakery-scripts'
        }
      },
      inputs: [{ name: 's3-feed' }],
      outputs: [{ name: 'book' }],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee s3-feed/stderr >&2)
          feed=s3-feed/distribution-feed.json
          echo -n "$(cat $feed | jq -r '.[-1].collection_id')" >book/collection_id
          echo -n "$(cat $feed | jq -r '.[-1].server')" >book/server
          echo -n "$(cat $feed | jq -r '.[-1].style')" >book/style
          echo -n "$(cat $feed | jq -r '.[-1].version')" >book/version
        `
        ]
      }
    }
  }
}

module.exports = task
