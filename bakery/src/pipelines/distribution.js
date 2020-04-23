const pipeline = (env) => {
  const taksLookUpFeed = require('../tasks/look-up-feed')
  const taskFetchBook = require('../tasks/fetch-book')
  const taskAssembleBook = require('../tasks/assemble-book')
  const taskAssembleBookMeta = require('../tasks/assemble-book-metadata')
  const taskBakeBook = require('../tasks/bake-book')
  const taskBakeBookMeta = require('../tasks/bake-book-metadata')
  const taskChecksumBook = require('../tasks/checksum-book')
  const taskDisassembleBook = require('../tasks/disassemble-book')
  const taskJsonifyBook = require('../tasks/jsonify-book')
  const taskUploadBook = require('../tasks/upload-book')

  const bucket = env.S3_DIST_BUCKET
  const awsAccessKeyId = '((aws-sandbox-secret-key-id))'
  const awsSecretAccessKey = '((aws-sandbox-secret-access-key))'

  const resources = [
    {
      name: 'cnx-recipes',
      type: 'git',
      source: {
        uri: 'https://github.com/openstax/cnx-recipes.git'
      }
    },
    {
      name: 's3-feed',
      type: 's3',
      source: {
        bucket: bucket,
        versioned_file: '((versioned-feed-file))',
        access_key_id: awsAccessKeyId,
        secret_access_key: awsSecretAccessKey
      }
    }
  ]

  const bakeryJob = {
    name: 'bakery',
    plan: [
      { get: 's3-feed', trigger: true, version: 'every' },
      { get: 'cnx-recipes' },
      taksLookUpFeed(),
      taskFetchBook(),
      taskAssembleBook(),
      taskAssembleBookMeta(),
      taskBakeBook(),
      taskBakeBookMeta(),
      taskChecksumBook(),
      taskDisassembleBook(),
      taskJsonifyBook(),
      taskUploadBook({
        bucketName: bucket,
        awsAccessKeyId: awsAccessKeyId,
        awsSecretAccessKey: awsSecretAccessKey
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
