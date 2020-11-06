const { constructImageSource } = require('../task-util/task-util')
const fs = require('fs')
const path = require('path')

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
  const shellScript = fs.readFileSync(path.resolve(__dirname, '../scripts/fetch_book_group.sh'), { encoding: "utf-8" })

  return {
    task: 'fetch book group',
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
      params: {
        BOOK_INPUT: bookInput,
        GH_SECRET_CREDS: githubSecretCreds,
        OUTPUT_NAME: outputName,
        BOOK_SLUGS_URL: bookSlugsUrl
      },
      run: {
        path: '/bin/sh',
        args: [
          '-cxe',
          shellScript
        ]
      }
    }
  }
}

module.exports = task
