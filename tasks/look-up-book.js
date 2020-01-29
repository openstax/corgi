const dedent = require('dedent')

const task = {
  task: 'look up book',
  config: {
    platform: 'linux',
    image_resource: {
      type: 'docker-image',
      source: {
        repository: 'openstax/nebuchadnezzar'
      }
    },
    inputs: [{ name: 'output-producer' }, { name: 'cnx-recipes' }],
    outputs: [{ name: 'book' }],
    run: {
      path: '/bin/bash',
      args: [
        '-cxe',
        /* eslint-disable no-template-curly-in-string */
        dedent`
          exec 2> >(tee book/stderr >&2)
          tail output-producer/*
          cp output-producer/id book/job_id
          cp output-producer/collection_id book/collection_id
          cp output-producer/version book/version
          cp output-producer/collection_style book/style
          cp output-producer/content_server book/server
          wget -q -O jq 'https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64' && chmod +x jq
          server_name="$(cat output-producer/job.json | ./jq -r '.content_server.name')"
          set +x
          . cnx-recipes/books.txt
          set -x
          for book_config in "${'${BOOK_CONFIGS[@]}'}"
          do
            read -r book_name recipe_name _ book_colid _ <<< "$book_config"
            if [ "$book_colid" == "$(cat book/collection_id)" ]
            then
              echo -n "$book_name" >book/name
            fi
          done
          echo -n "$(cat book/collection_id)-$(cat book/version)-${'${server_name}'}-$(cat book/job_id).pdf" >book/pdf_filename
          echo -n "https://ce-pdf-spike.s3.amazonaws.com/$(cat book/pdf_filename)" >book/pdf_url
          if [ ! -f book/name ]
          then
            set +x
            echo "Book not found" >book/stderr
            exit 1
          fi
        `
        /* eslint-enable */
      ]
    }
  }
}

module.exports = task
