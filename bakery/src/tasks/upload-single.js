const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const { awsAccessKeyId, awsSecretAccessKey, distBucket, codeVersion, distBucketPath } = taskArgs
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
  const bookInput = 'book'
  const jsonifiedInput = 'jsonified-single'
  const checksumInput = 'checksum-single'
  const resourceInput = 'fetched-book-group-resources'
  const uploadOutput = 'upload-single'
  const shellScript = fs.readFileSync(path.resolve(__dirname, '../scripts/upload_single.sh'), { encoding: 'utf-8' })

  return {
    task: 'upload single',
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
        { name: bookInput },
        { name: jsonifiedInput },
        { name: checksumInput },
        { name: resourceInput }
      ],
      outputs: [
        { name: uploadOutput }
      ],
      params: {
        BUCKET_PREFIX: distBucketPrefix,
        BOOK_INPUT: bookInput,
        JSONIFIED_INPUT: jsonifiedInput,
        CHECKSUM_INPUT: checksumInput,
        UPLOAD_OUTPUT: uploadOutput
      },
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          shellScript
        ]
      }
    }
  }
}

module.exports = task
