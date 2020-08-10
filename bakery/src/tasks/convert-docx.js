const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const imageDefault = {
    name: 'openstax/cops-bakery-scripts',
    tag: 'trunk'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })

  return {
    task: 'convert to docx',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      inputs: [
        { name: 'book' },
        { name: 'jsonified-book' }
      ],
      outputs: [{ name: 'docx-book' }],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee docx-book/stderr >&2)
          cp -r jsonified-book/* docx-book
          collection_id="$(cat book/collection_id)"
          book_dir="docx-book/$collection_id/jsonified"
          target_dir="docx-book/$collection_id/docx"
          mkdir "$target_dir"
          cd "$book_dir"
          for xhtmlfile in ./*@*.xhtml; do
            xhtmlfile_basename=$(basename "$xhtmlfile")
            metadata_filename="${'${xhtmlfile_basename%.*}'}".json
            docx_filename=$(cat "$metadata_filename" | jq -r '.slug').docx
            wrapped_tempfile="${'${xhtmlfile}'}.tmp"
            xsltproc --output "$wrapped_tempfile" /code/gdoc/wrap-in-table.xsl "$xhtmlfile"
            pandoc --reference-doc="/code/gdoc/custom-reference.docx" --from=html --to=docx --output="../../../$target_dir/$docx_filename" "$wrapped_tempfile"
          done
        `
        ]
      }
    }
  }
}

module.exports = task
