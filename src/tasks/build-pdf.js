const dedent = require('dedent')

const task = () => {
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
          book_dir="mathified-book/$(cat book/name)"
          prince -v --output="artifacts/$(cat book/pdf_filename)" "$book_dir/collection.mathified.xhtml"
        `
        ]
      }
    }
  }
}

module.exports = task
