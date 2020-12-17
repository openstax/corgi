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
  const taskPatchDisassembledLinks = require('../tasks/patch-disassembled-links')
  const taskJsonifyBook = require('../tasks/jsonify-book')
  const taskUploadBook = require('../tasks/upload-book')

  const taskFetchBookGroup = require('../tasks/fetch-book-group')
  const taskAssembleBookGroup = require('../tasks/assemble-book-group')
  const taskAssembleBookMetadataGroup = require('../tasks/assemble-book-metadata-group')
  const taskBakeBookGroup = require('../tasks/bake-book-group')
  const taskBakeBookMetadataGroup = require('../tasks/bake-book-metadata-group')
  const taskLinkSingle = require('../tasks/link-single')
  const taskDisassembleSingle = require('../tasks/disassemble-single')
  const taskPatchDisassembledLinksSingle = require('../tasks/patch-disassembled-links-single')
  const taskJsonifySingle = require('../tasks/jsonify-single')
  const taskUploadSingle = require('../tasks/upload-single')
  const taskMathifySingle = require('../tasks/mathify-single')
  const taskPdfifySingle = require('../tasks/pdfify-single')
  const taskGenPreviewUrls = require('../tasks/gen-preview-urls')

  const lockedTag = env.IMAGE_TAG || 'trunk'
  const awsAccessKeyId = env.S3_ACCESS_KEY_ID
  const awsSecretAccessKey = env.S3_SECRET_ACCESS_KEY
  const codeVersionFromTag = env.IMAGE_TAG || 'version-unknown'
  const imageOverrides = {
    tag: lockedTag,
    ...env.dockerCredentials
  }
  const buildLogRetentionDays = 14
  const distBucketPath = 'apps/archive-preview/'

  // FIXME: These mappings should be in the COPS resource
  const JobType = Object.freeze({
    PDF: 1,
    DIST_PREVIEW: 2,
    GIT_PDF: 3,
    GIT_DIST_PREVIEW: 4
  })
  const Status = Object.freeze({
    QUEUED: 1,
    ASSIGNED: 2,
    PROCESSING: 3,
    FAILED: 4,
    SUCCEEDED: 5
  })

  const reportToOutputProducer = (resource) => {
    return (status, extras) => {
      return {
        put: resource,
        params: {
          id: `${resource}/id`,
          status_id: status,
          ...extras
        }
      }
    }
  }

  const reportToOutputProducerPdf = reportToOutputProducer('output-producer-pdf')
  const reportToOutputProducerDistPreview = reportToOutputProducer('output-producer-dist-preview')
  const reportToOutputProducerGitPdf = reportToOutputProducer('output-producer-git-pdf')
  const reportToOutputProducerGitDistPreview = reportToOutputProducer('output-producer-git-dist-preview')

  const resourceTypes = [
    {
      name: 'output-producer',
      type: 'docker-image',
      source: {
        repository: 'openstax/output-producer-resource',
        ...imageOverrides
      }
    }
  ]

  const resources = [
    {
      name: 'cnx-recipes-output',
      type: 'docker-image',
      source: {
        repository: 'openstax/cnx-recipes-output',
        ...imageOverrides
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
      name: 'output-producer-git-pdf',
      type: 'output-producer',
      source: {
        api_root: env.COPS_TARGET,
        job_type_id: JobType.GIT_PDF,
        status_id: 1
      }
    },
    {
      name: 'output-producer-git-dist-preview',
      type: 'output-producer',
      source: {
        api_root: env.COPS_TARGET,
        job_type_id: JobType.GIT_DIST_PREVIEW,
        status_id: 1
      }
    },
    {
      name: 's3-pdf',
      type: 's3',
      source: {
        bucket: env.COPS_ARTIFACTS_S3_BUCKET,
        access_key_id: awsAccessKeyId,
        secret_access_key: awsSecretAccessKey,
        skip_download: true
      }
    }
  ]

  const gitPdfJob = {
    name: 'PDF (git)',
    build_log_retention: {
      days: buildLogRetentionDays
    },
    plan: [
      { get: 'output-producer-git-pdf', trigger: true, version: 'every' },
      reportToOutputProducerGitPdf(Status.ASSIGNED),
      { get: 'cnx-recipes-output' },
      taskLookUpBook({ inputSource: 'output-producer-git-pdf', image: imageOverrides, contentSource: 'git' }),
      reportToOutputProducerGitPdf(Status.PROCESSING),
      taskFetchBookGroup({
        image: imageOverrides,
        githubSecretCreds: env.GH_SECRET_CREDS
      }),
      taskAssembleBookGroup({ image: imageOverrides }),
      taskAssembleBookMetadataGroup({ image: imageOverrides }),
      taskBakeBookGroup({ image: imageOverrides }),
      taskBakeBookMetadataGroup({ image: imageOverrides }),
      taskLinkSingle({ image: imageOverrides }),
      taskMathifySingle({ image: imageOverrides }),
      taskPdfifySingle({ bucketName: env.COPS_ARTIFACTS_S3_BUCKET, image: imageOverrides }),
      {
        put: 's3-pdf',
        params: {
          file: 'artifacts-single/*.pdf',
          acl: 'public-read',
          content_type: 'application/pdf'
        }
      }
    ],
    on_success: reportToOutputProducerGitPdf(Status.SUCCEEDED, {
      pdf_url: 'artifacts-single/pdf_url'
    }),
    on_failure: reportToOutputProducerGitPdf(Status.FAILED),
    on_error: reportToOutputProducerGitPdf(Status.FAILED),
    on_abort: reportToOutputProducerGitPdf(Status.FAILED)
  }

  const pdfJob = {
    name: 'PDF',
    build_log_retention: {
      days: buildLogRetentionDays
    },
    plan: [
      { get: 'output-producer-pdf', trigger: true, version: 'every' },
      reportToOutputProducerPdf(Status.ASSIGNED),
      { get: 'cnx-recipes-output' },
      taskLookUpBook({ inputSource: 'output-producer-pdf', image: imageOverrides }),
      reportToOutputProducerPdf(Status.PROCESSING),
      taskFetchBook({ image: imageOverrides }),
      taskAssembleBook({ image: imageOverrides }),
      taskLinkExtras({
        image: imageOverrides,
        server: 'archive.cnx.org'
      }),
      taskBakeBook({ image: imageOverrides }),
      taskMathifyBook({ image: imageOverrides }),
      taskValidateXhtml({
        image: imageOverrides,
        inputSource: 'mathified-book',
        inputPath: 'collection.mathified.xhtml',
        validationNames: ['link-to-duplicate-id']
      }),
      taskBuildPdf({ bucketName: env.COPS_ARTIFACTS_S3_BUCKET, image: imageOverrides }),
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
    build_log_retention: {
      days: buildLogRetentionDays
    },
    plan: [
      { get: 'output-producer-dist-preview', trigger: true, version: 'every' },
      reportToOutputProducerDistPreview(Status.ASSIGNED),
      { get: 'cnx-recipes-output' },
      taskLookUpBook({ inputSource: 'output-producer-dist-preview', image: imageOverrides }),
      reportToOutputProducerDistPreview(Status.PROCESSING),
      taskFetchBook({ image: imageOverrides }),
      taskAssembleBook({ image: imageOverrides }),
      taskLinkExtras({
        image: imageOverrides,
        server: 'archive.cnx.org'
      }),
      taskAssembleBookMeta({ image: imageOverrides }),
      taskBakeBook({ image: imageOverrides }),
      taskBakeBookMeta({ image: imageOverrides }),
      taskChecksumBook({ image: imageOverrides }),
      taskDisassembleBook({ image: imageOverrides }),
      taskPatchDisassembledLinks({ image: imageOverrides }),
      taskJsonifyBook({ image: imageOverrides }),
      taskValidateXhtml({
        image: imageOverrides,
        inputSource: 'jsonified-book',
        inputPath: 'jsonified/*@*.xhtml',
        validationNames: ['duplicate-id', 'broken-link']
      }),
      taskUploadBook({
        image: imageOverrides,
        distBucket: env.COPS_ARTIFACTS_S3_BUCKET,
        distBucketPath: distBucketPath,
        awsAccessKeyId: awsAccessKeyId,
        awsSecretAccessKey: awsSecretAccessKey,
        codeVersion: codeVersionFromTag
      }),
      taskGenPreviewUrls({
        image: imageOverrides,
        distBucketPath: distBucketPath,
        codeVersion: codeVersionFromTag,
        jsonifiedInput: 'jsonified-book',
        cloudfrontUrl: env.COPS_CLOUDFRONT_URL
      })
    ],
    on_success: reportToOutputProducerDistPreview(Status.SUCCEEDED, {
      pdf_url: 'preview-urls/content_urls'
    }),
    on_failure: reportToOutputProducerDistPreview(Status.FAILED),
    on_error: reportToOutputProducerDistPreview(Status.FAILED),
    on_abort: reportToOutputProducerDistPreview(Status.FAILED)
  }

  const gitDistPreviewJob = {
    name: 'Distribution Preview (git)',
    build_log_retention: {
      days: buildLogRetentionDays
    },
    plan: [
      { get: 'output-producer-git-dist-preview', trigger: true, version: 'every' },
      reportToOutputProducerGitDistPreview(Status.ASSIGNED),
      { get: 'cnx-recipes-output' },
      taskLookUpBook({ inputSource: 'output-producer-git-dist-preview', image: imageOverrides, contentSource: 'git' }),
      reportToOutputProducerGitDistPreview(Status.PROCESSING),
      taskFetchBookGroup({
        image: imageOverrides,
        githubSecretCreds: env.GH_SECRET_CREDS
      }),
      taskAssembleBookGroup({ image: imageOverrides }),
      taskAssembleBookMetadataGroup({ image: imageOverrides }),
      taskBakeBookGroup({ image: imageOverrides }),
      taskBakeBookMetadataGroup({ image: imageOverrides }),
      taskLinkSingle({ image: imageOverrides }),
      taskDisassembleSingle({ image: imageOverrides }),
      taskPatchDisassembledLinksSingle({ image: imageOverrides }),
      taskJsonifySingle({
        image: imageOverrides
      }),
      taskValidateXhtml({
        image: imageOverrides,
        inputSource: 'jsonified-single',
        inputPath: '/*@*.xhtml',
        validationNames: ['duplicate-id', 'broken-link'],
        contentSource: 'git'
      }),
      taskUploadSingle({
        image: imageOverrides,
        distBucket: env.COPS_ARTIFACTS_S3_BUCKET,
        distBucketPath: distBucketPath,
        awsAccessKeyId: awsAccessKeyId,
        awsSecretAccessKey: awsSecretAccessKey,
        codeVersion: codeVersionFromTag
      }),
      taskGenPreviewUrls({
        image: imageOverrides,
        distBucketPath: distBucketPath,
        codeVersion: codeVersionFromTag,
        cloudfrontUrl: env.COPS_CLOUDFRONT_URL,
        jsonifiedInput: 'jsonified-single',
        contentSource: 'git'
      })
    ],
    on_success: reportToOutputProducerGitDistPreview(Status.SUCCEEDED, {
      pdf_url: 'preview-urls/content_urls'
    }),
    on_failure: reportToOutputProducerGitDistPreview(Status.FAILED),
    on_error: reportToOutputProducerGitDistPreview(Status.FAILED),
    on_abort: reportToOutputProducerGitDistPreview(Status.FAILED)
  }

  return {
    config: {
      resource_types: resourceTypes,
      resources: resources,
      jobs: [pdfJob, distPreviewJob, gitPdfJob, gitDistPreviewJob]
    }
  }
}

module.exports = pipeline
