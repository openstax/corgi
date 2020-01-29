const fs = require('fs')
const yaml = require('js-yaml')

const taskLookUpBook = require('./tasks/look-up-book')
const taskFetchBook = require('./tasks/fetch-book')
const taskAssembleBook = require('./tasks/assemble-book')
const taskBakeBook = require('./tasks/bake-book')
const taskMathifyBook = require('./tasks/mathify-book')
const taskBuildPdf = require('./tasks/build-pdf')

const outputFile = process.argv[2]

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
      tag: '1.1.1'
    }
  }
]

const resources = [
  {
    name: 'cnx-recipes',
    type: 'git',
    source: {
      uri: 'https://github.com/openstax/cnx-recipes.git'
    }
  },
  {
    name: 'output-producer',
    type: 'output-producer',
    source: {
      api_root: 'https://cops.cnx.org/api',
      status_id: 1
    }
  },
  {
    name: 's3',
    type: 's3',
    source: {
      bucket: 'ce-pdf-spike',
      access_key_id: '((aws-sandbox-secret-key-id))',
      secret_access_key: '((aws-sandbox-secret-access-key))',
      skip_download: true
    }
  }
]

const bakeryJob = {
  name: 'bakery',
  plan: [
    { get: 'output-producer', trigger: true, version: 'every' },
    reportToOutputProducer(Status.ASSIGNED),
    { get: 'cnx-recipes' },
    taskLookUpBook,
    reportToOutputProducer(Status.PROCESSING),
    taskFetchBook,
    taskAssembleBook,
    taskBakeBook,
    taskMathifyBook,
    taskBuildPdf,
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
    pdf_url: 'book/pdf_url'
  }),
  on_failure: reportToOutputProducer(Status.FAILED),
  on_error: reportToOutputProducer(Status.FAILED),
  on_abort: reportToOutputProducer(Status.FAILED)
}

const config = {
  resource_types: resourceTypes,
  resources: resources,
  jobs: [bakeryJob]
}

const info = `
########## This is a generated file ##########
# To generate a pipeline.yml file you
# can run 'yarn build [path/to/output-file]'
# from the 'bakery/' directory. If no path
# is specified, the output will be directed
# to stdout.
##############################################

`
const output = info + yaml.safeDump(config)

if (outputFile) {
  fs.writeFileSync(outputFile, output)
} else {
  console.log(output)
}
