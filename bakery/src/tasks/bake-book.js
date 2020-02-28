const dedent = require('dedent')

const task = () => {
  return {
    task: 'bake book',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: {
          repository: 'openstax/cnx-easybake'
        }
      },
      inputs: [
        { name: 'book' },
        { name: 'assembled-book' },
        { name: 'cnx-recipes' }
      ],
      outputs: [{ name: 'baked-book' }],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee baked-book/stderr >&2)
          cp -r assembled-book/* baked-book
          book_dir="baked-book/$(cat book/collection_id)"
          cnx-easybake -q "cnx-recipes/recipes/output/$(cat book/style).css" "$book_dir/collection.assembled.xhtml" "$book_dir/collection.baked.xhtml"
          style_file="cnx-recipes/styles/output/$(cat book/style)-pdf.css"
          if [ -f "$style_file" ]
          then
            cp "$style_file" $book_dir
            sed -i "s%<\\/head>%<link rel=\"stylesheet\" type=\"text/css\" href=\"$(basename $style_file)\" />&%" "$book_dir/collection.baked.xhtml"
          else
            echo "Warning: Style Not Found" >baked-book/stderr
          fi
        `
        ]
      }
    }
  }
}

module.exports = task
