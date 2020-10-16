const dedent = require('dedent')

const { constructImageSource } = require('../task-util/task-util')

const task = (taskArgs) => {
    const { server } = taskArgs
    const imageDefault = {
        name: 'openstax/cops-bakery-scripts',
        tag: 'trunk'
    }
    const imageOverrides = taskArgs != null && taskArgs.image != null ? taskArgs.image : {}
    const imageSource = constructImageSource({ ...imageDefault, ...imageOverrides })

    const bakedInput = 'baked-book-group'
    const bakedMetaInput = 'baked-book-metadata-group'

    return {
        task: 'link group',
        config: {
            platform: 'linux',
            image_resource: {
                type: 'docker-image',
                source: imageSource
            },
            inputs: [
                { name: bakedInput },
                { name: bakedMetaInput }
            ],
            outputs: [{ name: 'linked-extras' }],
            run: {
                path: '/bin/bash',
                args: [
                    '-cxe',
                    dedent`
                    exec 2> >(tee linked-extras/stderr >&2)
                    for collection in $(find "${bakedInput}/" -path *.baked.xhtml -type f); do
                        link-extras "${bakedInput}" ${server} "/code/scripts/canonical-book-list.json"
                    done
                    `
                ]
            }
        }
    }
}

module.exports = task
