const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const { bucketName } = taskArgs
  const imageDefault = {
    name: 'openstax/princexml',
    tag: 'master'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })

  return {
    task: 'build pdf',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      inputs: [
        { name: 'book' },
        { name: 'mathified-book' }
      ],
      outputs: [{ name: 'artifacts' }],
      run: {
        user: 'root',
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee artifacts/stderr >&2)
          book_dir="mathified-book/$(cat book/collection_id)"
          echo -n "https://${bucketName}.s3.amazonaws.com/$(cat book/pdf_filename)" >artifacts/pdf_url
          prince -v --output="artifacts/$(cat book/pdf_filename)" "$book_dir/collection.mathified.xhtml"
        `
        ]
      }
    }
  }
}

module.exports = task
