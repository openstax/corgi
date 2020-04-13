const dedent = require('dedent')

const task = () => {
  return {
    task: 'fetch book',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: {
          repository: 'openstax/nebuchadnezzar'
        }
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
