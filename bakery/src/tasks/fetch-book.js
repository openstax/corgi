const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const imageDefault = {
    name: 'openstax/nebuchadnezzar'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })

  return {
    task: 'fetch book',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      inputs: [{ name: 'book' }],
      outputs: [{ name: 'fetched-book' }],
      params: { COLUMNS: 80 },
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee fetched-book/stderr >&2)
          cd fetched-book
          book_dir="$(cat ../book/collection_id)"
          mkdir -p "$book_dir" ~/.config/
          server="$(cat ../book/server)"
          cat >~/.config/nebuchadnezzar.ini <<EOF
          [settings]
          [environ-$server]
          url = https://$server
          EOF
          yes | neb get -r -m -d "$book_dir/raw" "$(cat ../book/server)" "$(cat ../book/collection_id)" "$(cat ../book/version)"
        `
        ]
      }
    }
  }
}

module.exports = task
