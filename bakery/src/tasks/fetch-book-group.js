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
  const outputName = 'fetched-book-group'
  return {
    task: 'fetch book',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      inputs: [{ name: 'book' }],
      outputs: [{ name: outputName }],
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
          book_dir="./${outputName}/$(cat $book_info/slug)"
          mkdir "$book_dir"
          reference=$(cat $book_info/version)
          [[ "$reference" = latest ]] && reference=master
          set +x
          # Do not show creds
          remote="https://${'${GH_SECRET_CREDS}'}@github.com/openstax/$(cat $book_info/repo).git"
          git clone --depth 1 "$remote" --branch "$reference" "$book_dir/raw"
          set -x
          wget ${bookSlugsUrl} -O "$book_dir/book-slugs.json"
        `
        ]
      }
    }
  }
}

module.exports = task
