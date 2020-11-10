const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const { bucketName } = taskArgs
  const imageDefault = {
    name: 'openstax/princexml',
    tag: 'trunk'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })

  const bookInput = 'book'
  const fetchedInput = 'fetched-book-group'
  const fetchedResourcesInput = 'fetched-book-group-resources'
  const symlinkInput = 'module-symlinks'
  const styleInput = 'group-style'
  const mathifiedInput = 'mathified-single'
  const artifactsOutput = 'artifacts-single'

  return {
    task: 'build pdf',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      inputs: [
        { name: bookInput },
        { name: fetchedInput },
        { name: fetchedResourcesInput },
        { name: styleInput },
        { name: symlinkInput },
        { name: mathifiedInput }
      ],
      outputs: [{ name: artifactsOutput }],
      run: {
        user: 'root',
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee ${artifactsOutput}/stderr >&2)

          # Inject symlinks and style so that princexml can use them
          find "${symlinkInput}" -type l | xargs -I{} cp -P {} "${mathifiedInput}"
          cp ${styleInput}/* ${mathifiedInput}

          echo -n "https://${bucketName}.s3.amazonaws.com/$(cat ${bookInput}/pdf_filename)" > ${artifactsOutput}/pdf_url
          prince -v --output="${artifactsOutput}/$(cat ${bookInput}/pdf_filename)" "${mathifiedInput}/$(cat ${bookInput}/slug).mathified.xhtml"
        `
        ]
      }
    }
  }
}

module.exports = task
