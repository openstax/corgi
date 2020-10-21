const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
    const imageDefault = {
        name: 'openstax/cops-bakery-scripts',
        tag: 'trunk'
    }
    const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
    const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })
    const fetchedInput = 'fetched-book-group'
    const assembledInput = 'assembled-book-group'
    const outputName = 'assembled-book-metadata-group'

    return {
        task: 'assemble book metadata',
        config: {
            platform: 'linux',
            image_resource: {
                type: 'docker-image',
                source: imageSource
            },
            inputs: [
                { name: fetchedInput },
                { name: assembledInput }
            ],
            outputs: [{ name: outputName }],
            run: {
                path: '/bin/bash',
                args: [
                    '-cxe',
                    dedent`
                    exec 2> >(tee ${outputName}/stderr >&2)
                    for collection in $(find "${assembledInput}/" -path *.assembled.xhtml -type f); do
                        slug_name=$(basename "$collection" | awk -F'[.]' '{ print $1; }')


                        echo "{" > uuid-to-revised-map.json
                        find ${fetchedInput}/raw/modules -path */m*/metadata.json | xargs cat | jq -r '. | "\"\(.id)\": \"\(.revised)\","' >> uuid-to-revised-map.json
                        echo '"dummy": "dummy"' >> uuid-to-revised-map.json
                        echo "}" >> uuid-to-revised-map.json

                        assemble-meta "${assembledInput}/$slug_name.assembled.xhtml" uuid-to-revised-map.json "${outputName}/$slug_name.assembled-metadata.json"
                    done
                    `
                ]
            }
        }
    }
}

module.exports = task
