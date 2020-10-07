const pipeline = (env) => {
  const taskLookUpBook = require('../tasks/look-up-book')
  const taskFetchBook = require('../tasks/fetch-book')
  const taskAssembleBook = require('../tasks/assemble-book')
  const taskLinkExtras = require('../tasks/link-extras')
  const taskBakeBook = require('../tasks/bake-book')
  const taskMathifyBook = require('../tasks/mathify-book')
  const taskBuildPdf = require('../tasks/build-pdf')
  const taskValidateXhtml = require('../tasks/validate-xhtml')

  const taskAssembleBookMeta = require('../tasks/assemble-book-metadata')
  const taskBakeBookMeta = require('../tasks/bake-book-metadata')
  const taskChecksumBook = require('../tasks/checksum-book')
  const taskDisassembleBook = require('../tasks/disassemble-book')
  const taskJsonifyBook = require('../tasks/jsonify-book')
  const taskUploadBook = require('../tasks/upload-book')

  const lockedTag = env.IMAGE_TAG || 'trunk'
  const awsAccessKeyId = env.S3_ACCESS_KEY_ID
  const awsSecretAccessKey = env.S3_SECRET_ACCESS_KEY
  const codeVersionFromTag = env.IMAGE_TAG || 'version-unknown'

  // FIXME: These mappings should be in the COPS resource
  const JobType = Object.freeze({
    PDF: 1,
    DIST_PREVIEW: 2
  })
  const Status = Object.freeze({
    QUEUED: 1,
    ASSIGNED: 2,
    PROCESSING: 3,
    FAILED: 4,
    SUCCEEDED: 5
  })

  const reportToOutputProducerPdf = (status, extras) => {
    return {
      put: 'output-producer-pdf',
      params: {
        id: 'output-producer-pdf/id',
        status_id: status,
        ...extras
      }
    }
  }

  const reportToOutputProducerDistPreview = (status, extras) => {
    return {
      put: 'output-producer-dist-preview',
      params: {
        id: 'output-producer-dist-preview/id',
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
        tag: lockedTag
      }
    }
  ]

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
      name: 'output-producer-pdf',
      type: 'output-producer',
      source: {
        api_root: env.COPS_TARGET,
        job_type_id: JobType.PDF,
        status_id: 1
      }
    },
    {
      name: 'output-producer-dist-preview',
      type: 'output-producer',
      source: {
        api_root: env.COPS_TARGET,
        job_type_id: JobType.DIST_PREVIEW,
        status_id: 1
      }
    },
    {
      name: 's3-pdf',
      type: 's3',
      source: {
        bucket: env.S3_COPS_ARTIFACTS_BUCKET,
        access_key_id: awsAccessKeyId,
        secret_access_key: awsSecretAccessKey,
        skip_download: true
      }
    }
  ]

  const pdfJob = {
    name: 'PDF',
    plan: [
      { get: 'output-producer-pdf', trigger: true, version: 'every' },
      reportToOutputProducerPdf(Status.ASSIGNED),
      { get: 'cnx-recipes-output' },
      taskLookUpBook({ inputSource: 'output-producer-pdf', image: { tag: lockedTag } }),
      reportToOutputProducerPdf(Status.PROCESSING),
      taskFetchBook({ image: { tag: lockedTag } }),
      taskAssembleBook({ image: { tag: lockedTag } }),
      taskLinkExtras({
        image: { tag: lockedTag },
        server: 'archive.cnx.org'
      }),
      taskBakeBook({ image: { tag: lockedTag } }),
      taskMathifyBook({ image: { tag: lockedTag } }),
      taskValidateXhtml({
        image: { tag: lockedTag },
        inputSource: 'mathified-book',
        inputPath: 'collection.mathified.xhtml',
        validationNames: ['link-to-duplicate-id']
      }),
      taskBuildPdf({ bucketName: env.S3_COPS_ARTIFACTS_BUCKET, image: { tag: lockedTag } }),
      {
        put: 's3-pdf',
        params: {
          file: 'artifacts/*.pdf',
          acl: 'public-read',
          content_type: 'application/pdf'
        }
      }
    ],
    on_success: reportToOutputProducerPdf(Status.SUCCEEDED, {
      pdf_url: 'artifacts/pdf_url'
    }),
    on_failure: reportToOutputProducerPdf(Status.FAILED),
    on_error: reportToOutputProducerPdf(Status.FAILED),
    on_abort: reportToOutputProducerPdf(Status.FAILED)
  }

  const distPreviewJob = {
    name: 'Distribution Preview',
    plan: [
      { get: 'output-producer-dist-preview', trigger: true, version: 'every' },
      reportToOutputProducerDistPreview(Status.ASSIGNED),
      { get: 'cnx-recipes-output' },
      taskLookUpBook({ inputSource: 'output-producer-dist-preview', image: { tag: lockedTag } }),
      reportToOutputProducerDistPreview(Status.PROCESSING),
      taskFetchBook({ image: { tag: lockedTag } }),
      taskAssembleBook({ image: { tag: lockedTag } }),
      taskLinkExtras({
        image: { tag: lockedTag },
        server: 'archive.cnx.org'
      }),
      taskAssembleBookMeta({ image: { tag: lockedTag } }),
      taskBakeBook({ image: { tag: lockedTag } }),
      taskBakeBookMeta({ image: { tag: lockedTag } }),
      taskChecksumBook({ image: { tag: lockedTag } }),
      taskDisassembleBook({ image: { tag: lockedTag } }),
      taskJsonifyBook({ image: { tag: lockedTag } }),
      taskValidateXhtml({
        image: { tag: lockedTag },
        inputSource: 'jsonified-book',
        inputPath: 'jsonified/*@*.xhtml',
        validationNames: ['duplicate-id', 'broken-link']
      }),
      taskUploadBook({
        distBucket: env.S3_COPS_ARTIFACTS_BUCKET,
        distBucketPath: 'apps/archive-preview/',
        awsAccessKeyId: awsAccessKeyId,
        awsSecretAccessKey: awsSecretAccessKey,
        codeVersion: codeVersionFromTag,
        updateQueueState: false,
        image: { tag: lockedTag }
      })
    ],
    on_success: reportToOutputProducerDistPreview(Status.SUCCEEDED, {
      pdf_url: 'upload-book/toc-s3-link-json'
    }),
    on_failure: reportToOutputProducerDistPreview(Status.FAILED),
    on_error: reportToOutputProducerDistPreview(Status.FAILED),
    on_abort: reportToOutputProducerDistPreview(Status.FAILED)
  }

  return {
    config: {
      resource_types: resourceTypes,
      resources: resources,
      jobs: [pdfJob, distPreviewJob]
    }
  }
}

module.exports = pipeline
