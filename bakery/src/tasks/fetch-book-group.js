const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const { githubSecretCreds } = taskArgs
  const imageDefault = {
    name: 'alpine/git',
    tag: 'latest'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })
  const bookSlugsUrl = 'https://raw.githubusercontent.com/openstax/content-manager-approved-books/master/book-slugs.json'

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
      params: {
        COLUMNS: 80,
        GH_SECRET_CREDS: githubSecretCreds
      },
      run: {
        path: '/bin/sh',
        args: [
          '-cxe',
          dedent`
          book_info=$(cd book && pwd)
          book_dir="./fetched-book/$(cat $book_info/collection_id)"
          mkdir "$book_dir"
          set +x
          # Do not show creds
          remote=https://${'${GH_SECRET_CREDS}'}@github.com/openstax/ce-git-storage-spike.git
          git clone "$remote" "$book_dir/raw"
          set -x
          set +e
          # FIXME: add assertion that checkout occurred
          git --git-dir="$book_dir/raw/.git" checkout "$(cat $book_info/version)"
          git --git-dir="$book_dir/raw/.git" checkout "v$(cat $book_info/version)"
          set -e
          wget ${bookSlugsUrl} -O "$book_dir/book-slugs.json"
        `
        ]
      }
    }
  }
}

module.exports = task
