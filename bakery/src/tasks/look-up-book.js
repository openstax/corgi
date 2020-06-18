const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const imageDefault = {
    name: 'openstax/nebuchadnezzar',
    tag: 'master'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })

  return {
    task: 'look up book',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      inputs: [{ name: 'output-producer' }],
      outputs: [{ name: 'book' }],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          /* eslint-disable no-template-curly-in-string */
          dedent`
          exec 2> >(tee book/stderr >&2)
          tail output-producer/*
          cp output-producer/id book/job_id
          cp output-producer/collection_id book/collection_id
          cp output-producer/version book/version
          cp output-producer/collection_style book/style
          cp output-producer/content_server book/server
          wget -q -O jq 'https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64' && chmod +x jq
          server_shortname="$(cat output-producer/job.json | ./jq -r '.content_server.name')"
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
