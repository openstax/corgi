const pipeline = (env) => {
  const taskLookUpFeed = require('../tasks/look-up-feed')
  const taskFetchBook = require('../tasks/fetch-book')
  const taskAssembleBook = require('../tasks/assemble-book')
  const taskAssembleBookMeta = require('../tasks/assemble-book-metadata')
  const taskBakeBook = require('../tasks/bake-book')
  const taskBakeBookMeta = require('../tasks/bake-book-metadata')
  const taskChecksumBook = require('../tasks/checksum-book')
  const taskDisassembleBook = require('../tasks/disassemble-book')
  const taskJsonifyBook = require('../tasks/jsonify-book')
  const taskUploadBook = require('../tasks/upload-book')

  const awsAccessKeyId = env.ENV_NAME === 'local' ? env.S3_ACCESS_KEY_ID : '((aws-sandbox-secret-key-id))'
  const awsSecretAccessKey = env.ENV_NAME === 'local' ? env.S3_SECRET_ACCESS_KEY : '((aws-sandbox-secret-access-key))'

  const resources = [
    {
      name: 'cnx-recipes-output',
      type: 'docker-image',
      source: {
        repository: 'openstax/cnx-recipes-output',
        tag: env.IMAGE_TAG || 'latest'
      }
    },
    {
      name: 's3-feed',
      type: 's3',
      source: {
        bucket: env.S3_DIST_BUCKET,
        versioned_file: env.VERSIONED_FILE,
        access_key_id: awsAccessKeyId,
        secret_access_key: awsSecretAccessKey
      }
    }
  ]

  const bakeryJob = {
    name: 'bakery',
    plan: [
      { get: 's3-feed', trigger: true, version: 'every' },
      { get: 'cnx-recipes-output' },
      taskLookUpFeed({
        versionedFile: env.VERSIONED_FILE,
        image: { tag: env.IMAGE_TAG }
      }),
      taskFetchBook({ image: { tag: env.IMAGE_TAG } }),
      taskAssembleBook({ image: { tag: env.IMAGE_TAG } }),
      taskAssembleBookMeta({ image: { tag: env.IMAGE_TAG } }),
      taskBakeBook({ image: { tag: env.IMAGE_TAG } }),
      taskBakeBookMeta({ image: { tag: env.IMAGE_TAG } }),
      taskChecksumBook({ image: { tag: env.IMAGE_TAG } }),
      taskDisassembleBook({ image: { tag: env.IMAGE_TAG } }),
      taskJsonifyBook({ image: { tag: env.IMAGE_TAG } }),
      taskUploadBook({
        bucketName: env.S3_DIST_BUCKET,
        awsAccessKeyId: awsAccessKeyId,
        awsSecretAccessKey: awsSecretAccessKey,
        image: { tag: env.IMAGE_TAG }
      })
    ]
  }

  return {
    config: {
      resources: resources,
      jobs: [bakeryJob]
    }
  }
}

module.exports = pipeline
