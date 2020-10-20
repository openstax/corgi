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

  const bookInput = 'book'
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
      inputs: [{ name: bookInput }],
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
          reference=$(cat ${bookInput}/version)
          [[ "$reference" = latest ]] && reference=master
          set +x
          # Do not show creds
          remote="https://${'${GH_SECRET_CREDS}'}@github.com/openstax/$(cat ${bookInput}/repo).git"
          git clone --depth 1 "$remote" --branch "$reference" "${outputName}/raw"
          set -x
          wget ${bookSlugsUrl} -O "${outputName}/book-slugs.json"
        `
        ]
      }
    }
  }
}

module.exports = task
