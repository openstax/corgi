const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
    const { inputSource, inputPath, contentSource: maybeContentSource } = taskArgs
    const imageDefault = {
      name: 'openstax/cops-bakery-scripts',
      tag: 'trunk'
    }
    const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
    const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })
    const contentSource = maybeContentSource != null ? maybeContentSource : 'archive'

  return {
    task: 'link rex',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      inputs: [
        { name: 'book' },
        { name: `${inputSource}` }
      ],
      outputs: [
        { name: 'artifacts' },
        { name: 'common-log' }
      ],
      run: {
        user: 'root',
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec > >(tee common-log/log >&2) 2>&1
          case $CONTENT_SOURCE in
            archive)
              collection_id="$(cat book/collection_id)"
              xhtmlfiles_path="${inputSource}/$collection_id/"${inputPath}
              ;;
            git)
              xhtmlfiles_path="${inputSource}"${inputPath}
              ;;
            *)
              echo "CONTENT_SOURCE unrecognized: $CONTENT_SOURCE"
              exit 1
              ;;
          esac
          book_slugs_file="/tmp/book-slugs.json"
          cat "$book_dir/approved-book-list.json" | jq ".approved_books|map(.books)|flatten" > "$book_slugs_file"
          for xhtmlfile in $xhtmlfiles_path
          do
            link-rex "$xhtmlfile" "$book_slugs_file"
          done
        `
        ]
      }
    }
  }
}

module.exports = task
