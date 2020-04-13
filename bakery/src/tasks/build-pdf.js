const dedent = require('dedent')

const task = ({ bucketName }) => {
  return {
    task: 'build pdf',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: {
          repository: 'openstax/princexml'
        }
      },
      inputs: [
        { name: 'book' },
        { name: 'mathified-book' }
      ],
      outputs: [{ name: 'artifacts' }],
      run: {
        user: 'root',
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee artifacts/stderr >&2)
          book_dir="mathified-book/$(cat book/collection_id)"
          echo -n "https://${bucketName}.s3.amazonaws.com/$(cat book/pdf_filename))" >artifacts/pdf_url
          prince -v --output="artifacts/$(cat book/pdf_filename)" "$book_dir/collection.mathified.xhtml"
        `
        ]
      }
    }
  }
}

module.exports = task
