const pipeline = (env) => {
  const taskCheckFeed = require('../tasks/check-feed')
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
  const codeVersionFromTag = env.IMAGE_TAG || 'version-unknown'
  const versionedFile = `${codeVersionFromTag}.${env.VERSIONED_FILE}`

  const lockedTag = env.IMAGE_TAG || 'master'

  const resources = [
    {
      name: 'cnx-recipes-output',
      type: 'docker-image',
      source: {
        repository: 'openstax/cnx-recipes-output',
        tag: lockedTag
      }
    },
    {
      name: 's3-feed',
      type: 's3',
      source: {
        bucket: env.S3_VERSIONED_BUCKET,
        versioned_file: versionedFile,
        initial_version: 'initializing',
        access_key_id: awsAccessKeyId,
        secret_access_key: awsSecretAccessKey
      }
    },
    {
      name: 'ticker',
      type: 'time',
      source: {
        interval: env.PIPELINE_TICK_INTERVAL
      }
    }
  ]

  const feederJob = {
    name: 'feeder',
    plan: [
      { get: 'ticker', trigger: true },
      taskCheckFeed({
        awsAccessKeyId: awsAccessKeyId,
        awsSecretAccessKey: awsSecretAccessKey,
        feedFileUrl: env.FEED_FILE_URL,
        versionedBucketName: env.S3_VERSIONED_BUCKET,
        versionedFile: versionedFile,
        codeVersion: codeVersionFromTag,
        maxBooksPerRun: env.MAX_BOOKS_PER_TICK,
        image: { tag: lockedTag }
      })
    ]
  }

  const bakeryJob = {
    name: 'bakery',
    plan: [
      { get: 's3-feed', trigger: true, version: 'every' },
      { get: 'cnx-recipes-output' },
      taskLookUpFeed({
        versionedFile: versionedFile,
        image: { tag: lockedTag }
      }),
      taskFetchBook({ image: { tag: lockedTag } }),
      taskAssembleBook({ image: { tag: lockedTag } }),
      taskAssembleBookMeta({ image: { tag: lockedTag } }),
      taskBakeBook({ image: { tag: lockedTag } }),
      taskBakeBookMeta({ image: { tag: lockedTag } }),
      taskChecksumBook({ image: { tag: lockedTag } }),
      taskDisassembleBook({ image: { tag: lockedTag } }),
      taskJsonifyBook({ image: { tag: lockedTag } }),
      taskUploadBook({
        distBucketName: env.S3_DIST_BUCKET,
        versionedBucketName: env.S3_VERSIONED_BUCKET,
        awsAccessKeyId: awsAccessKeyId,
        awsSecretAccessKey: awsSecretAccessKey,
        codeVersion: codeVersionFromTag,
        image: { tag: lockedTag }
      })
    ]
  }

  return {
    config: {
      resources: resources,
      jobs: [feederJob, bakeryJob]
    }
  }
}

module.exports = pipeline
