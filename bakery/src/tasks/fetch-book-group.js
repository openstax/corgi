const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const { githubSecretCreds } = taskArgs
  const imageDefault = {
    name: 'openstax/cops-bakery-scripts',
    tag: 'trunk'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })

  const bookInput = 'book'
  const bookSlugsUrl = 'https://raw.githubusercontent.com/openstax/content-manager-approved-books/master/book-slugs.json'
  const contentOutput = 'fetched-book-group'
  const resourceOutput = 'fetched-book-group-resources'

  return {
    task: 'fetch book',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      inputs: [{ name: bookInput }],
      outputs: [
        { name: contentOutput },
        { name: resourceOutput }
      ],
      params: {
        COLUMNS: 80,
        GH_SECRET_CREDS: githubSecretCreds
      },
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          reference=$(cat ${bookInput}/version)
          [[ "$reference" = latest ]] && reference=master
          set +x
          # Do not show creds
          remote="https://$GH_SECRET_CREDS@github.com/openstax/$(cat ${bookInput}/repo).git"
          git clone --depth 1 "$remote" --branch "$reference" "${contentOutput}/raw"
          set -x
          if [[ ! -f "${contentOutput}/raw/collections/$(cat ${bookInput}/slug).collection.xml" ]]; then
            echo "No matching book for slug in this repo"
            exit 1
          fi
          rm -rf "${contentOutput}/raw/.git"
          wget ${bookSlugsUrl} -O "${contentOutput}/book-slugs.json"
          mv "${contentOutput}/raw/media" "${resourceOutput}/."
          fetch-map-resources "${contentOutput}/raw/modules" "../../../../${resourceOutput}/media"
        `
        ]
      }
    }
  }
}

module.exports = task
