const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const imageDefault = {
    name: 'openstax/nebuchadnezzar',
    tag: 'trunk'
  }
  const { inputSource, image } = taskArgs
  const imageOverrides = image != null ? image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })

  return {
    task: 'look up book',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      inputs: [{ name: inputSource }],
      outputs: [{ name: 'book' }],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          /* eslint-disable no-template-curly-in-string */
          dedent`
          exec 2> >(tee book/stderr >&2)
          tail ${inputSource}/*
          cp ${inputSource}/id book/job_id
          cp ${inputSource}/collection_id book/collection_id
          cp ${inputSource}/version book/version
          cp ${inputSource}/collection_style book/style
          cp ${inputSource}/content_server book/server
          wget -q -O jq 'https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64' && chmod +x jq
          server_shortname="$(cat ${inputSource}/job.json | ./jq -r '.content_server.name')"
          echo "$server_shortname" >book/server_shortname
          pdf_filename="$(cat book/collection_id)-$(cat book/version)-$(cat book/server_shortname)-$(cat book/job_id).pdf"
          echo "$pdf_filename" > book/pdf_filename
        `
        /* eslint-enable */
        ]
      }
    }
  }
}

module.exports = task
