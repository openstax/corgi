const pipeline = (env) => {
  const taskLookUpBook = require('../tasks/look-up-book')
  const taskFetchBook = require('../tasks/fetch-book')
  const taskAssembleBook = require('../tasks/assemble-book')
  const taskBakeBook = require('../tasks/bake-book')
  const taskMathifyBook = require('../tasks/mathify-book')
  const taskBuildPdf = require('../tasks/build-pdf')

  // FIXME: This mapping should be in the COPS resource
  const Status = Object.freeze({
    QUEUED: 1,
    ASSIGNED: 2,
    PROCESSING: 3,
    FAILED: 4,
    SUCCEEDED: 5
  })

  const reportToOutputProducer = (status, extras) => {
    return {
      put: 'output-producer',
      params: {
        id: 'output-producer/id',
        status_id: status,
        ...extras
      }
    }
  }

  const resourceTypes = [
    {
      name: 'output-producer',
      type: 'docker-image',
      source: {
        repository: 'openstax/output-producer-resource',
        tag: env.IMAGE_TAG || 'latest'
      }
    }
  ]

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
      name: 'output-producer',
      type: 'output-producer',
      source: {
        api_root: env.COPS_TARGET,
        status_id: 1
      }
    },
    {
      name: 's3',
      type: 's3',
      source: {
        bucket: env.S3_BUCKET,
        access_key_id: env.ENV_NAME === 'local'
          ? env.S3_ACCESS_KEY_ID
          : '((aws-sandbox-secret-key-id))',
        secret_access_key: env.ENV_NAME === 'local'
          ? env.S3_SECRET_ACCESS_KEY
          : '((aws-sandbox-secret-access-key))',
        skip_download: true
      }
    }
  ]

  const bakeryJob = {
    name: 'bakery',
    plan: [
      { get: 'output-producer', trigger: true, version: 'every' },
      reportToOutputProducer(Status.ASSIGNED),
      { get: 'cnx-recipes-output' },
      taskLookUpBook({ image: { tag: env.IMAGE_TAG } }),
      reportToOutputProducer(Status.PROCESSING),
      taskFetchBook({ image: { tag: env.IMAGE_TAG } }),
      taskAssembleBook({ image: { tag: env.IMAGE_TAG } }),
      taskBakeBook({ image: { tag: env.IMAGE_TAG } }),
      taskMathifyBook({ image: { tag: env.IMAGE_TAG } }),
      taskBuildPdf({ bucketName: env.S3_BUCKET, image: { tag: env.IMAGE_TAG } }),
      {
        put: 's3',
        params: {
          file: 'artifacts/*.pdf',
          acl: 'public-read',
          content_type: 'application/pdf'
        }
      }
    ],
    on_success: reportToOutputProducer(Status.SUCCEEDED, {
      pdf_url: 'artifacts/pdf_url'
    }),
    on_failure: reportToOutputProducer(Status.FAILED),
    // TODO: Uncomment this when upgrading to concourse >=5.0.1
    // on_error: reportToOutputProducer(Status.FAILED),
    on_abort: reportToOutputProducer(Status.FAILED)
  }

  return {
    config: {
      resource_types: resourceTypes,
      resources: resources,
      jobs: [bakeryJob]
    }
  }
}

module.exports = pipeline
