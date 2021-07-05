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
  const bookSlugsUrl = 'https://raw.githubusercontent.com/openstax/content-manager-approved-books/master/approved-book-list.json'

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
        { name: `${inputSource}` },
        { name: 'common-log' }
      ],
      params: {
        CONTENT_SOURCE: contentSource
      },
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
              book_dir="${inputSource}/$collection_id"
              abl_file="$book_dir/approved-book-list.json"
              target_dir="${inputSource}/$collection_id"
              ;;
            git)
              xhtmlfiles_path="${inputSource}/"${inputPath}
              abl_file=/tmp/approved-book-list.json
              wget ${bookSlugsUrl} -O $abl_file
              target_dir="${inputSource}"
              ;;
            *)
              echo "CONTENT_SOURCE unrecognized: $CONTENT_SOURCE"
              exit 1
              ;;
          esac
          book_slugs_file="/tmp/book-slugs.json"
          cat $abl_file | jq ".approved_books|map(.books)|flatten" > "$book_slugs_file"
          cat $book_slugs_file
          for xhtmlfile in $xhtmlfiles_path
          do
            link-rex "$xhtmlfile" "$book_slugs_file" "$target_dir"
          done
        `
        ]
      }
    }
  }
}

module.exports = task
