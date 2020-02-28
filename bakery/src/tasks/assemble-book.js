const dedent = require('dedent')

const task = () => {
  return {
    task: 'assemble book',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: {
          repository: 'openstax/nebuchadnezzar'
        }
      },
      inputs: [
        { name: 'book' },
        { name: 'fetched-book' }
      ],
      outputs: [{ name: 'assembled-book' }],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee assembled-book/stderr >&2)
          cp -r fetched-book/* assembled-book
          cd assembled-book
          book_dir="../assembled-book/$(cat ../book/collection_id)"
          neb assemble "$book_dir/raw" "$book_dir"
        `
        ]
      }
    }
  }
}

module.exports = task
