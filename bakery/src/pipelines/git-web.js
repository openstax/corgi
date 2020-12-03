const pipeline = (env) => {
    const taskCheckFeed = require('../tasks/check-feed')
    const taskDequeueBook = require('../tasks/dequeue-book')
    const taskFetchBook = require('../tasks/fetch-book-group')
    const taskAssembleBook = require('../tasks/assemble-book-group')
    const taskLinkExtras = require('../tasks/link-single')
    const taskAssembleBookMeta = require('../tasks/assemble-book-metadata-group')
    const taskBakeBook = require('../tasks/bake-book-group')
    const taskBakeBookMeta = require('../tasks/bake-book-metadata-group')
    const taskChecksumBook = require('../tasks/checksum-single')
    const taskDisassembleBook = require('../tasks/disassemble-single')
    const taskJsonifyBook = require('../tasks/jsonify-single')
    const taskValidateXhtml = require('../tasks/validate-xhtml')
    const taskUploadBook = require('../tasks/upload-single')

    const awsAccessKeyId = env.S3_ACCESS_KEY_ID
    const awsSecretAccessKey = env.S3_SECRET_ACCESS_KEY
    const codeVersionFromTag = env.IMAGE_TAG || 'version-unknown'
    const githubSecretCreds = env.GH_SECRET_CREDS
    const queueFilename = `${codeVersionFromTag}.${env.DIST_QUEUE_FILENAME}`
    const queueStatePrefix = 'dist'

    const lockedTag = env.IMAGE_TAG || 'trunk'

    const imageOverrides = {
        tag: lockedTag,
        ...env.dockerCredentials
    }

    console.log(env.dockerCredentials)

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
            name: 's3-queue',
            type: 's3',
            source: {
                bucket: env.DIST_QUEUE_STATE_S3_BUCKET,
                versioned_file: queueFilename,
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
                feedFileUrl: env.DIST_FEED_FILE_URL,
                queueStateBucket: env.DIST_QUEUE_STATE_S3_BUCKET,
                queueFilename: queueFilename,
                codeVersion: codeVersionFromTag,
                maxBooksPerRun: env.MAX_BOOKS_PER_TICK,
                statePrefix: queueStatePrefix,
                image: imageOverrides
            })
        ]
    }

    const bakeryJob = {
        name: 'bakery',
        max_in_flight: 5,
        plan: [
            { get: 's3-queue', trigger: true, version: 'every' },
            { get: 'cnx-recipes-output' },
            taskDequeueBook({
                queueFilename: queueFilename,
                image: imageOverrides
            }),
            taskFetchBook({
                githubSecretCreds: githubSecretCreds,
                image: imageOverrides
            }),
            taskAssembleBook({ image: imageOverrides }),
            taskAssembleBookMeta({ image: imageOverrides }),
            taskBakeBook({ image: imageOverrides }),
            taskBakeBookMeta({ image: imageOverrides }),
            taskLinkExtras({ image: imageOverrides }),
            taskChecksumBook({
                image: imageOverrides,
                inputSource: 'fetched-book-group-resources',
            }),
            taskDisassembleBook({ image: imageOverrides }),
            taskJsonifyBook({
                image: imageOverrides
            }),
            taskValidateXhtml({
                image: imageOverrides,
                inputSource: 'jsonified-single',
                inputPath: '/*@*.xhtml',
                validationNames: ['duplicate-id', 'broken-link']
            }),
            taskUploadBook({
                distBucket: env.DIST_S3_BUCKET,
                distBucketPath: 'apps/archive/',
                queueStateBucket: env.DIST_QUEUE_STATE_S3_BUCKET,
                awsAccessKeyId: awsAccessKeyId,
                awsSecretAccessKey: awsSecretAccessKey,
                codeVersion: codeVersionFromTag,
                statePrefix: queueStatePrefix,
                image: imageOverrides
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