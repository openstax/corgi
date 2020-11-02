const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
  const imageDefault = {
    name: 'openstax/cops-bakery-scripts',
    tag: 'trunk'
  }
  const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
  const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })

  const bookInput = 'book'
  const fetchedInput = 'fetched-book-group'
  const bakedInput = 'baked-book-group'
  const bakedMetaInput = 'baked-book-metadata-group'
  const linkedOutput = 'linked-single'

  return {
    task: 'link group',
    config: {
      platform: 'linux',
      image_resource: {
        type: 'docker-image',
        source: imageSource
      },
      inputs: [
        { name: bookInput },
        { name: fetchedInput },
        { name: bakedInput },
        { name: bakedMetaInput }
      ],
      outputs: [{ name: linkedOutput }],
      run: {
        path: '/bin/bash',
        args: [
          '-cxe',
          dedent`
          exec 2> >(tee ${linkedOutput}/stderr >&2)
          echo "{" > module-canonicals.json
          find ${fetchedInput}/raw/modules/ -path *metadata.json | xargs cat | jq -r '. | "\"\(.id)\": \"\(.canonical)\","' >> module-canonicals.json
          echo '"dummy": "dummy"' >> module-canonicals.json
          echo "}" >> module-canonicals.json

          link-single "${bakedInput}" "${bakedMetaInput}" "$(cat ${bookInput}/slug)" "${fetchedInput}/book-slugs.json" module-canonicals.json "${linkedOutput}/$(cat ${bookInput}/slug).linked.xhtml"
          `
        ]
      }
    }
  }
}

module.exports = task
