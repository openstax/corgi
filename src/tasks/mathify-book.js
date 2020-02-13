const dedent = require('dedent')

const task = () => {
  return {
    task: 'mathify book',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: {
          repository: 'openstax/mathify'
        }
      },
      inputs: [
        { name: 'book' },
        { name: 'baked-book' }
      ],
      outputs: [{ name: 'mathified-book' }],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee mathified-book/stderr >&2)
          cp -r baked-book/* mathified-book
          book_dir=mathified-book/$(cat book/name)
          node /src/typeset/start -i "$book_dir/collection.baked.xhtml" -o "$book_dir/collection.mathified.xhtml" -f svg  
        `
        ]
      }
    }
  }
}

module.exports = task
